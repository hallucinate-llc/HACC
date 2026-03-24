from unittest import mock

import compare_complaint_manager_interfaces as module
import hacc_complaint_manager as manager


def test_extract_json_object_from_text_finds_embedded_payload():
    payload = manager._extract_json_object_from_text("warning line\n{\"tools\": [{\"name\": \"complaint.review_case\"}]}\n")

    assert payload["tools"][0]["name"] == "complaint.review_case"


def test_compare_interfaces_reports_matching_sets():
    tool_payload = {
        "tools": [
            {"name": "complaint.list_intake_questions"},
            {"name": "complaint.review_case"},
        ]
    }
    interface_payload = {
        "package": {"module": "complaint_generator", "service_class": "ComplaintWorkspaceService"},
        "cli": {"module": "complaint_generator.cli", "script_name": "complaint-workspace"},
        "mcp": {"module": "complaint_generator.mcp_server", "script_name": "complaint-mcp-server"},
    }
    with (
        mock.patch.object(module, "complaint_manager_interfaces", return_value=interface_payload),
        mock.patch.object(module, "list_workspace_tools_via_package", return_value=tool_payload),
        mock.patch.object(module, "list_workspace_tools_via_mcp", return_value=tool_payload),
        mock.patch.object(module, "list_workspace_tools_via_cli", return_value=tool_payload),
    ):
        summary = module.compare_interfaces()

    assert summary["interfaces"] == interface_payload
    assert summary["all_interfaces_match"] is True
    assert summary["shared_tool_count"] == 2
    assert summary["package_only"] == []
    assert summary["mcp_only"] == []
    assert summary["cli_only"] == []
