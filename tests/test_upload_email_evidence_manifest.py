from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

import upload_email_evidence_manifest as module


def test_upload_manifest_saves_all_records(tmp_path: Path) -> None:
    manifest_path = tmp_path / "email_import_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "mediator_evidence_records": [
                    {
                        "title": "Termination Notice",
                        "content": "Saved email: /tmp/message.eml",
                        "source": "gmail_import",
                        "attachment_names": ["notice.pdf"],
                    },
                    {
                        "title": "Hearing Request",
                        "content": "Saved email: /tmp/hearing.eml",
                        "source": "gmail_import",
                        "attachment_names": [],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    service = mock.Mock()
    service.save_evidence.side_effect = [
        {"saved": {"id": "documents-1", "attachment_names": ["notice.pdf"]}},
        {"saved": {"id": "documents-2", "attachment_names": []}},
    ]

    with mock.patch.object(module, "create_workspace_service", return_value=service):
        result = module.upload_manifest(
            str(manifest_path),
            user_id="case-user",
            claim_element_id="causation",
        )

    assert result["status"] == "success"
    assert result["uploaded_count"] == 2
    assert result["uploaded"][0]["saved_id"] == "documents-1"
    assert result["uploaded"][1]["saved_id"] == "documents-2"
    service.save_evidence.assert_any_call(
        "case-user",
        kind="document",
        claim_element_id="causation",
        title="Termination Notice",
        content="Saved email: /tmp/message.eml",
        source="gmail_import",
        attachment_names=["notice.pdf"],
    )


def test_upload_manifest_can_include_review_payload(tmp_path: Path) -> None:
    manifest_path = tmp_path / "email_import_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "mediator_evidence_records": [
                    {
                        "title": "Termination Notice",
                        "content": "Saved email: /tmp/message.eml",
                        "source": "gmail_import",
                        "attachment_names": ["notice.pdf"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    service = mock.Mock()
    service.save_evidence.return_value = {"saved": {"id": "documents-1", "attachment_names": ["notice.pdf"]}}
    service.call_mcp_tool.return_value = {"support_matrix": [{"id": "causation", "supported": True}]}

    with mock.patch.object(module, "create_workspace_service", return_value=service):
        result = module.upload_manifest(
            str(manifest_path),
            user_id="case-user",
            claim_element_id="causation",
            review_after_upload=True,
        )

    assert result["review"]["support_matrix"][0]["supported"] is True
    service.call_mcp_tool.assert_called_once_with("complaint.review_case", {"user_id": "case-user"})


def test_upload_manifest_can_generate_and_export(tmp_path: Path) -> None:
    manifest_path = tmp_path / "email_import_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "mediator_evidence_records": [
                    {
                        "title": "Termination Notice",
                        "content": "Saved email: /tmp/message.eml",
                        "source": "gmail_import",
                        "attachment_names": ["notice.pdf"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    service = mock.Mock()
    service.save_evidence.return_value = {"saved": {"id": "documents-1", "attachment_names": ["notice.pdf"]}}
    service.generate_complaint.return_value = {"draft": {"title": "Complaint"}}
    service.export_complaint_packet.return_value = {"packet_summary": {"title": "Complaint"}}
    service.export_complaint_markdown.return_value = {"artifact": {"format": "markdown"}}

    with mock.patch.object(module, "create_workspace_service", return_value=service):
        result = module.upload_manifest(
            str(manifest_path),
            user_id="case-user",
            claim_element_id="causation",
            generate_after_upload=True,
            export_packet_after_upload=True,
            export_markdown_after_upload=True,
        )

    assert result["generated_complaint"]["draft"]["title"] == "Complaint"
    assert result["exported_packet"]["packet_summary"]["title"] == "Complaint"
    assert result["exported_markdown"]["artifact"]["format"] == "markdown"
    service.generate_complaint.assert_called_once_with("case-user", use_llm=False)
    service.export_complaint_packet.assert_called_once_with("case-user")
    service.export_complaint_markdown.assert_called_once_with("case-user")
