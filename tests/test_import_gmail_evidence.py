from __future__ import annotations

import argparse
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
    address_file.write_text(
        "# comment\nManager <manager@example.org>\n\nTENANT@example.com\n",
        encoding="utf-8",
    )

    targets = module._load_address_targets(["lawyer@example.com"], [str(address_file)])

    assert targets == {"manager@example.org", "tenant@example.com", "lawyer@example.com"}


def test_load_address_targets_handles_empty_inputs() -> None:
    assert module._load_address_targets([], []) == set()


def test_build_search_criteria_supports_date_and_subject_helpers() -> None:
    args = SimpleNamespace(
        search='FROM "manager@example.org"',
        since_date="2026-01-01",
        before_date="2026-02-01",
        subject_contains="termination",
    )

    assert module._build_search_criteria(args) == (
        '(FROM "manager@example.org") SINCE "1-Jan-2026" BEFORE "1-Feb-2026" SUBJECT "termination"'
    )


def test_build_search_criteria_defaults_to_all() -> None:
    args = SimpleNamespace(search="ALL", since_date=None, before_date=None, subject_contains=None)

    assert module._build_search_criteria(args) == "ALL"


def test_quote_imap_mailbox_handles_spaces_and_quotes() -> None:
    assert module._quote_imap_mailbox('[Gmail]/All Mail') == '"[Gmail]/All Mail"'
    assert module._quote_imap_mailbox('Folder "A"') == '"Folder \\"A\\""'


def test_build_complaint_terms_combines_query_and_keyword_files(tmp_path: Path) -> None:
    keyword_file = tmp_path / "keywords.txt"
    keyword_file.write_text("# comment\ntermination notice\nretaliation\n", encoding="utf-8")
    args = SimpleNamespace(
        complaint_query="hearing request denial after eviction notice",
        complaint_keyword=["accommodation"],
        complaint_keyword_file=[str(keyword_file)],
    )

    terms = module._build_complaint_terms(args)

    assert "hearing" in terms
    assert "termination" in terms
    assert "retaliation" in terms
    assert "accommodation" in terms


def test_score_message_relevance_prefers_subject_hits() -> None:
    message = EmailMessage()
    message["Subject"] = "Termination Notice"
    message["From"] = "manager@example.org"
    message["To"] = "tenant@example.com"
    message.set_content("This email discusses a hearing request and retaliation timeline.")

    score = module._score_message_relevance(message, ["termination", "hearing", "retaliation"])

    assert score["score"] >= 5.0
    assert "subject" in score["matched_fields"]
    assert "body" in score["matched_fields"]
    assert "termination" in score["matched_terms"]


def test_is_oversized_search_error_detects_imap_limit() -> None:
    assert module._is_oversized_search_error(module.imaplib.IMAP4.error("got more than 1000000 bytes"))
    assert not module._is_oversized_search_error(module.imaplib.IMAP4.error("other failure"))


def test_resolve_auth_mode_defaults_to_gmail_app_password_for_gmail_server() -> None:
    args = SimpleNamespace(auth_mode=None, use_gmail_oauth=False, server="imap.gmail.com")
    assert module._resolve_auth_mode(args) == "gmail_app_password"


def test_resolve_auth_mode_defaults_to_plain_imap_for_other_servers() -> None:
    args = SimpleNamespace(auth_mode=None, use_gmail_oauth=False, server="mail.example.org")
    assert module._resolve_auth_mode(args) == "imap_password"


def test_resolve_auth_mode_honors_explicit_mode() -> None:
    args = SimpleNamespace(auth_mode="gmail_oauth", use_gmail_oauth=False, server="mail.example.org")
    assert module._resolve_auth_mode(args) == "gmail_oauth"


def test_humanize_connection_error_for_gmail_app_password() -> None:
    message = module._humanize_connection_error(
        ConnectionError(
            "Failed to connect to IMAP server: b'[ALERT] Application-specific password required: https://support.google.com/accounts/answer/185833 (Failure)'"
        )
    )

    assert "requires an app password" in message
    assert "16-character app password" in message


def test_run_allows_gmail_oauth_without_password() -> None:
    args = SimpleNamespace(
        username="user@gmail.com",
        password=None,
        use_gmail_oauth=True,
        gmail_oauth_client_secrets="/tmp/client.json",
        gmail_oauth_token_cache="/tmp/token.json",
        no_browser=True,
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
        since_date=None,
        before_date=None,
        subject_contains=None,
        case_slug="demo",
        output_dir="evidence/email_imports",
        server="imap.gmail.com",
        port=993,
        timeout=30,
        no_ssl=False,
        limit=None,
        upload_to_workspace=False,
        review_after_upload=False,
        generate_after_upload=False,
        export_packet_after_upload=False,
        export_markdown_after_upload=False,
        dry_run=False,
        user_id="case-user",
        claim_element_id="notice",
    )

    with mock.patch.object(module, "import_gmail_evidence", return_value={"status": "success"}) as import_mock:
        result = module.anyio.run(module._run, args)

    assert result == 0
    forwarded_args = import_mock.call_args.args[0]
    assert forwarded_args.username == "user@gmail.com"
    assert forwarded_args.password is None
    assert forwarded_args.use_gmail_oauth is True


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
    parser = module.build_parser()
    args = parser.parse_args([])
    args.username = None
    args.password = None
    args.prompt_credentials = True
    args.prompt_password = False
    args.use_keyring = False
    args.save_to_keyring = False
    args.folder = None

    async def _fake_run(_parsed_args):
        if not _parsed_args.folder:
            _parsed_args.folder = [module.DEFAULT_GMAIL_FOLDER]
        return 0

    with (
        mock.patch.object(module, "build_parser", return_value=parser),
        mock.patch.object(parser, "parse_args", return_value=args),
        mock.patch.object(
            module,
            "resolve_gmail_credentials",
            return_value=("user@gmail.com", "secret-app-password"),
        ),
        mock.patch.object(module, "_run", _fake_run),
    ):
        result = module.main([])

    assert result == 0
    assert args.username == "user@gmail.com"
    assert args.password == "secret-app-password"
    assert args.folder == [module.DEFAULT_GMAIL_FOLDER]


def test_run_uses_prompt_password_when_username_already_set() -> None:
    parser = module.build_parser()
    args = parser.parse_args([])
    args.username = "user@gmail.com"
    args.password = None
    args.prompt_credentials = False
    args.prompt_password = True
    args.use_keyring = False
    args.save_to_keyring = False
    args.folder = ["INBOX"]

    async def _fake_run(_parsed_args):
        return 0

    with (
        mock.patch.object(module, "build_parser", return_value=parser),
        mock.patch.object(parser, "parse_args", return_value=args),
        mock.patch.object(
            module,
            "resolve_gmail_credentials",
            return_value=("user@gmail.com", "secret-app-password"),
        ),
        mock.patch.object(module, "_run", _fake_run),
    ):
        result = module.main([])

    assert result == 0
    assert args.username == "user@gmail.com"
    assert args.password == "secret-app-password"

def test_main_can_use_keyring_resolution(monkeypatch) -> None:
    parser = module.build_parser()
    args = parser.parse_args([])
    args.username = "user@gmail.com"
    args.password = ""
    args.prompt_credentials = False
    args.prompt_password = False
    args.use_keyring = True
    args.save_to_keyring = False
    args.folder = ["INBOX"]

    monkeypatch.setattr(module, "build_parser", lambda: parser)
    monkeypatch.setattr(parser, "parse_args", lambda argv=None: args)
    monkeypatch.setattr(module, "resolve_gmail_credentials", lambda **kwargs: ("user@gmail.com", "stored-app-password"))
    async def _fake_run(_parsed_args):
        return 0

    monkeypatch.setattr(module, "_run", _fake_run)

    result = module.main([])

    assert result == 0


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


def test_fetch_folder_messages_falls_back_to_recent_sequence_numbers_on_oversized_search() -> None:
    message = _build_sample_message()
    raw_bytes = message.as_bytes(policy=email.policy.default)
    fetched_ids: list[bytes] = []

    class _FakeConnection:
        def select(self, _folder: str, readonly: bool = True) -> tuple[str, list[bytes]]:
            assert readonly is True
            return "OK", [b"200"]

        def search(self, _charset: None, _criteria: str) -> tuple[str, list[bytes]]:
            raise module.imaplib.IMAP4.error("command: SEARCH => got more than 1000000 bytes")

        def fetch(self, msg_id: bytes, _spec: str) -> tuple[str, list[tuple[None, bytes]]]:
            fetched_ids.append(msg_id)
            return "OK", [(None, raw_bytes)]

    processor = SimpleNamespace(connection=_FakeConnection())

    async def _run_fetch() -> list[tuple[bytes, EmailMessage]]:
        return await module._fetch_folder_messages(
            processor,
            folder="[Gmail]/All Mail",
            limit=3,
            search_criteria="ALL",
        )

    rows = module.anyio.run(_run_fetch)

    assert len(rows) == 3
    assert fetched_ids == [b"198", b"199", b"200"]


def test_import_gmail_evidence_filters_by_complaint_relevance(tmp_path: Path) -> None:
    relevant = EmailMessage()
    relevant["Subject"] = "Termination hearing request"
    relevant["From"] = "manager@example.org"
    relevant["To"] = "starworks5@gmail.com"
    relevant["Message-ID"] = "<relevant@example.org>"
    relevant.set_content("Retaliation and denial details.")

    irrelevant = EmailMessage()
    irrelevant["Subject"] = "Weekly deals"
    irrelevant["From"] = "store@example.org"
    irrelevant["To"] = "starworks5@gmail.com"
    irrelevant["Message-ID"] = "<irrelevant@example.org>"
    irrelevant.set_content("Shoes and clothes.")

    class _FakeProcessor:
        def __init__(self, **_kwargs: object) -> None:
            self.connection = object()

        async def connect(self) -> None:
            return None

        async def disconnect(self) -> None:
            return None

        def _parse_email_message(self, message: EmailMessage, include_attachments: bool = True) -> dict[str, object]:
            return {
                "subject": message.get("Subject", ""),
                "from": message.get("From", ""),
                "to": message.get("To", ""),
                "cc": message.get("Cc", ""),
                "date": "2026-03-24T00:00:00+00:00",
                "message_id_header": message.get("Message-ID", ""),
                "attachments": [],
            }

    args = SimpleNamespace(
        address=["starworks5@gmail.com"],
        address_file=[],
        from_address=[],
        from_address_file=[],
        to_address=[],
        to_address_file=[],
        complaint_query="termination hearing retaliation",
        complaint_keyword=[],
        complaint_keyword_file=[],
        min_relevance_score=2.0,
        search="ALL",
        since_date=None,
        before_date=None,
        subject_contains=None,
        output_dir=str(tmp_path),
        case_slug="demo",
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
        limit=10,
        dry_run=True,
    )

    async def _run_import() -> dict[str, object]:
        with (
            mock.patch.object(module, "EmailProcessor", _FakeProcessor),
            mock.patch.object(
                module,
                "_fetch_folder_messages",
                return_value=[
                    (relevant.as_bytes(policy=email.policy.default), relevant),
                    (irrelevant.as_bytes(policy=email.policy.default), irrelevant),
                ],
            ),
        ):
            return await module.import_gmail_evidence(args)

    result = module.anyio.run(_run_import)

    assert result["matched_email_count"] == 1
    assert result["preview"][0]["subject"] == "Termination hearing request"
