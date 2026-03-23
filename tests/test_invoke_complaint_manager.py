import json
from subprocess import CompletedProcess
from unittest import mock

import invoke_complaint_manager as module


def test_package_interface_invokes_workspace_tool(capsys):
    with mock.patch.object(module, "call_workspace_tool", return_value={"ok": True}) as call_mock:
        exit_code = module.main(["package", "--tool", "complaint.list_intake_questions"])

    assert exit_code == 0
    call_mock.assert_called_once_with("complaint.list_intake_questions", {})
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True


def test_mcp_interface_invokes_jsonrpc_wrapper(capsys):
    with mock.patch.object(module, "call_workspace_mcp", return_value={"jsonrpc": "2.0", "id": 7}) as call_mock:
        exit_code = module.main(
            ["mcp", "--tool", "complaint.build_mediator_prompt", "--arguments-json", '{"user_id":"demo"}', "--request-id", "7"]
        )

    assert exit_code == 0
    call_mock.assert_called_once_with("complaint.build_mediator_prompt", {"user_id": "demo"}, request_id=7)
    payload = json.loads(capsys.readouterr().out)
    assert payload["id"] == 7


def test_cli_interface_forwards_args(capsys):
    completed = CompletedProcess(["python"], 0, stdout='{"tools":[]}\n', stderr="")
    with mock.patch.object(module, "run_workspace_cli", return_value=completed) as run_mock:
        exit_code = module.main(["cli", "--", "tools"])

    assert exit_code == 0
    run_mock.assert_called_once_with(["tools"])
    assert '{"tools":[]}' in capsys.readouterr().out


def test_package_interface_requires_tool():
    try:
        module.main(["package"])
    except ValueError as exc:
        assert str(exc) == "--tool is required for package and mcp interfaces."
    else:
        raise AssertionError("expected ValueError when tool is omitted")
