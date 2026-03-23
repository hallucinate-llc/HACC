#!/usr/bin/env python3
"""Shared accessors for the current complaint manager interfaces."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict


REPO_ROOT = Path(__file__).resolve().parent
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
COMPLAINT_GENERATOR_PACKAGE = "complaint_generator"
COMPLAINT_WORKSPACE_SCRIPT = "complaint-workspace"
COMPLAINT_WORKSPACE_ALIASES = ["complaint-generator-workspace"]
COMPLAINT_MCP_SERVER_SCRIPT = "complaint-mcp-server"
COMPLAINT_MCP_SERVER_ALIASES = ["complaint-generator-mcp"]


def ensure_complaint_generator_on_path() -> None:
    root = str(COMPLAINT_GENERATOR_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def complaint_manager_interfaces() -> Dict[str, Any]:
    return {
        "package": {
            "module": COMPLAINT_GENERATOR_PACKAGE,
            "service_class": "ComplaintWorkspaceService",
            "lazy_exports": [
                "ComplaintWorkspaceService",
                "complaint_cli_main",
                "complaint_mcp_server_main",
                "handle_jsonrpc_message",
                "tool_list_payload",
            ],
            "mcp_handler_module": f"{COMPLAINT_GENERATOR_PACKAGE}.mcp",
            "mcp_handler": "handle_jsonrpc_message",
            "mcp_tool_list": "tool_list_payload",
            "workspace_module": f"{COMPLAINT_GENERATOR_PACKAGE}.workspace",
            "workspace_helpers": [
                "start_session",
                "submit_intake_answers",
                "save_evidence",
                "generate_complaint",
                "list_mcp_tools",
            ],
        },
        "cli": {
            "module": f"{COMPLAINT_GENERATOR_PACKAGE}.cli",
            "module_entrypoint": f"{COMPLAINT_GENERATOR_PACKAGE}.cli:main",
            "module_command": "python -m complaint_generator.cli --help",
            "implementation_module": "applications.complaint_cli",
            "script_name": COMPLAINT_WORKSPACE_SCRIPT,
            "script_aliases": list(COMPLAINT_WORKSPACE_ALIASES),
            "entrypoint": "main",
            "example_commands": [
                "complaint-workspace tools",
                "complaint-workspace mediator-prompt --user-id demo-user",
                "complaint-workspace export-packet --user-id demo-user",
            ],
        },
        "mcp": {
            "module": f"{COMPLAINT_GENERATOR_PACKAGE}.mcp_server",
            "module_entrypoint": f"{COMPLAINT_GENERATOR_PACKAGE}.mcp_server:main",
            "module_command": "python -m complaint_generator.mcp_server",
            "implementation_module": "applications.complaint_mcp_server",
            "protocol_module": f"{COMPLAINT_GENERATOR_PACKAGE}.mcp",
            "entrypoint": "main",
            "transport": "stdio-jsonrpc",
            "script_name": COMPLAINT_MCP_SERVER_SCRIPT,
            "launcher_alias": COMPLAINT_MCP_SERVER_ALIASES[0],
            "launcher_aliases": list(COMPLAINT_MCP_SERVER_ALIASES),
            "request_handler": "handle_jsonrpc_message",
            "tool_list_function": "tool_list_payload",
        },
    }


def create_workspace_service() -> Any:
    ensure_complaint_generator_on_path()
    from complaint_generator import ComplaintWorkspaceService

    return ComplaintWorkspaceService()


def list_workspace_mcp_tools() -> Dict[str, Any]:
    ensure_complaint_generator_on_path()
    from complaint_generator.mcp import tool_list_payload

    return tool_list_payload(create_workspace_service())
