#!/usr/bin/env python3
"""Compare complaint manager tool surfaces across package, MCP, and CLI interfaces."""

from __future__ import annotations

import json
from typing import Dict, Set

from hacc_complaint_manager import (
    complaint_manager_interfaces,
    list_workspace_tools_via_cli,
    list_workspace_tools_via_mcp,
    list_workspace_tools_via_package,
)


def _tool_names(payload: Dict[str, object]) -> Set[str]:
    names: Set[str] = set()
    for item in list(payload.get("tools") or []):
        if isinstance(item, dict):
            name = str(item.get("name") or "").strip()
            if name:
                names.add(name)
    return names


def compare_interfaces() -> Dict[str, object]:
    interfaces_payload = complaint_manager_interfaces()
    package_payload = list_workspace_tools_via_package()
    mcp_payload = list_workspace_tools_via_mcp()
    cli_payload = list_workspace_tools_via_cli()

    package_names = _tool_names(package_payload)
    mcp_names = _tool_names(mcp_payload)
    cli_names = _tool_names(cli_payload)
    shared = sorted(package_names & mcp_names & cli_names)
    union = package_names | mcp_names | cli_names
    return {
        "interfaces": interfaces_payload,
        "package_tool_count": len(package_names),
        "mcp_tool_count": len(mcp_names),
        "cli_tool_count": len(cli_names),
        "shared_tool_count": len(shared),
        "shared_tools": shared,
        "package_only": sorted(package_names - (mcp_names | cli_names)),
        "mcp_only": sorted(mcp_names - (package_names | cli_names)),
        "cli_only": sorted(cli_names - (package_names | mcp_names)),
        "all_interfaces_match": package_names == mcp_names == cli_names,
        "union_tool_count": len(union),
    }


def main() -> int:
    print(json.dumps(compare_interfaces(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
