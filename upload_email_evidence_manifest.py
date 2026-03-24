#!/usr/bin/env python3
"""Upload imported email evidence records into the complaint workspace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from hacc_complaint_manager import create_workspace_service


def _load_manifest(path: str) -> dict[str, Any]:
    manifest_path = Path(path).expanduser().resolve()
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def upload_manifest(
    manifest_path: str,
    *,
    user_id: str,
    claim_element_id: str,
    source: str = "gmail_import",
    review_after_upload: bool = False,
    generate_after_upload: bool = False,
    export_packet_after_upload: bool = False,
    export_markdown_after_upload: bool = False,
) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    service = create_workspace_service()
    uploaded: list[dict[str, Any]] = []

    for record in list(manifest.get("mediator_evidence_records") or []):
        result = service.save_evidence(
            user_id,
            kind="document",
            claim_element_id=claim_element_id,
            title=str(record.get("title") or "Imported email evidence"),
            content=str(record.get("content") or ""),
            source=str(record.get("source") or source),
            attachment_names=[str(item) for item in list(record.get("attachment_names") or [])],
        )
        uploaded.append(
            {
                "title": str(record.get("title") or ""),
                "saved_id": ((result.get("saved") or {}).get("id") or ""),
                "attachment_names": list((result.get("saved") or {}).get("attachment_names") or []),
            }
        )

    result = {
        "status": "success",
        "manifest_path": str(Path(manifest_path).expanduser().resolve()),
        "user_id": user_id,
        "claim_element_id": claim_element_id,
        "uploaded_count": len(uploaded),
        "uploaded": uploaded,
    }
    if review_after_upload:
        result["review"] = service.call_mcp_tool("complaint.review_case", {"user_id": user_id})
    if generate_after_upload:
        result["generated_complaint"] = service.generate_complaint(user_id, use_llm=False)
    if export_packet_after_upload:
        result["exported_packet"] = service.export_complaint_packet(user_id)
    if export_markdown_after_upload:
        result["exported_markdown"] = service.export_complaint_markdown(user_id)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Upload a Gmail email-import manifest into the complaint workspace evidence store."
    )
    parser.add_argument("manifest_path", help="Path to email_import_manifest.json")
    parser.add_argument("--user-id", default="demo-user", help="Complaint workspace user id")
    parser.add_argument(
        "--claim-element-id",
        default="causation",
        help="Claim element bucket to associate with the imported email evidence",
    )
    parser.add_argument("--source", default="gmail_import", help="Evidence source label")
    parser.add_argument(
        "--review-after-upload",
        action="store_true",
        help="Call complaint.review_case after uploading and include the review payload.",
    )
    parser.add_argument(
        "--generate-after-upload",
        action="store_true",
        help="Generate a complaint draft after upload and include the draft payload.",
    )
    parser.add_argument(
        "--export-packet-after-upload",
        action="store_true",
        help="Export the complaint packet after upload and include the packet payload.",
    )
    parser.add_argument(
        "--export-markdown-after-upload",
        action="store_true",
        help="Export complaint markdown after upload and include the markdown payload.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = upload_manifest(
        args.manifest_path,
        user_id=args.user_id,
        claim_element_id=args.claim_element_id,
        source=args.source,
        review_after_upload=args.review_after_upload,
        generate_after_upload=args.generate_after_upload,
        export_packet_after_upload=args.export_packet_after_upload,
        export_markdown_after_upload=args.export_markdown_after_upload,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
