from unittest import mock

import hacc_complaint_manager as module


def test_complaint_manager_interfaces_expose_package_cli_and_mcp() -> None:
    payload = module.complaint_manager_interfaces()

    assert payload["package"]["module"] == "complaint_generator"
    assert payload["package"]["service_class"] == "ComplaintWorkspaceService"
    assert payload["package"]["mcp_handler_module"] == "complaint_generator.mcp"
    assert payload["package"]["workspace_module"] == "complaint_generator.workspace"
    assert "generate_complaint" in payload["package"]["workspace_helpers"]
    assert payload["cli"]["module"] == "applications.complaint_cli"
    assert payload["cli"]["module_entrypoint"] == "applications.complaint_cli:main"
    assert payload["cli"]["module_command"] == "python -m applications.complaint_cli --help"
    assert payload["cli"]["compatibility_module"] == "complaint_generator.cli"
    assert payload["cli"]["script_name"] == "complaint-workspace"
    assert payload["mcp"]["module"] == "applications.complaint_mcp_server"
    assert payload["mcp"]["module_entrypoint"] == "applications.complaint_mcp_server:main"
    assert payload["mcp"]["module_command"] == "python -m applications.complaint_mcp_server"
    assert payload["mcp"]["compatibility_module"] == "complaint_generator.mcp_server"
    assert payload["mcp"]["protocol_module"] == "complaint_generator.mcp"
    assert payload["mcp"]["script_name"] == "complaint-mcp-server"
    assert payload["mcp"]["launcher_alias"] == "complaint-generator-mcp"
    assert payload["mcp"]["server_info_name"] == "complaint-workspace-mcp"


def test_handle_workspace_mcp_message_uses_public_protocol_surface() -> None:
    response = module.handle_workspace_mcp_message(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        }
    )

    assert response is not None
    assert response["result"]["serverInfo"]["name"] == "complaint-workspace-mcp"


def test_run_workspace_cli_uses_current_cli_implementation_module() -> None:
    with mock.patch.object(module.subprocess, "run", return_value=mock.Mock(returncode=0, stdout="", stderr="")) as run_mock:
        module.run_workspace_cli(["tools"])

    command = run_mock.call_args.args[0]
    kwargs = run_mock.call_args.kwargs
    assert command[:3] == [module.sys.executable, "-m", "applications.complaint_cli"]
    assert command[3:] == ["tools"]
    assert kwargs["cwd"] == str(module.COMPLAINT_GENERATOR_ROOT)
    assert str(module.COMPLAINT_GENERATOR_ROOT) in kwargs["env"]["PYTHONPATH"]
