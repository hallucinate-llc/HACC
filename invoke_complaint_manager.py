#!/usr/bin/env python3
"""Invoke the complaint manager through package, MCP, or CLI interfaces."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, List

from hacc_complaint_manager import (
    call_workspace_mcp,
    call_workspace_tool,
    complaint_manager_interfaces,
    run_workspace_cli,
)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Invoke the complaint manager through its package, MCP, or CLI interface.",
    )
    parser.add_argument("interface", choices=("package", "mcp", "cli"))
    parser.add_argument("--tool", default="", help="Complaint tool name for package/mcp modes.")
    parser.add_argument(
        "--arguments-json",
        default="{}",
        help="JSON object of tool arguments for package/mcp modes.",
    )
    parser.add_argument(
        "--request-id",
        type=int,
        default=1,
        help="JSON-RPC request id for MCP mode.",
    )
    parser.add_argument(
        "--show-interfaces",
        action="store_true",
        help="Print the current complaint manager interface contract before invoking.",
    )
    return parser


def _parse_arguments_json(raw: str) -> dict[str, Any]:
    payload = json.loads(raw or "{}")
    if not isinstance(payload, dict):
        raise ValueError("--arguments-json must decode to a JSON object.")
    return payload


def main(argv: List[str] | None = None) -> int:
    parser = create_parser()
    args, remainder = parser.parse_known_args(argv)

    if args.show_interfaces:
        print(json.dumps(complaint_manager_interfaces(), indent=2, sort_keys=True))

    if args.interface == "cli":
        cli_args = list(remainder or [])
        if cli_args and cli_args[0] == "--":
            cli_args = cli_args[1:]
        result = run_workspace_cli(cli_args)
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return int(result.returncode)

    if not args.tool.strip():
        raise ValueError("--tool is required for package and mcp interfaces.")

    tool_arguments = _parse_arguments_json(args.arguments_json)
    if args.interface == "package":
        print(json.dumps(call_workspace_tool(args.tool, tool_arguments), indent=2, sort_keys=True))
        return 0

    print(json.dumps(call_workspace_mcp(args.tool, tool_arguments, request_id=args.request_id), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
