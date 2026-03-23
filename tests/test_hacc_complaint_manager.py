import hacc_complaint_manager as module


def test_complaint_manager_interfaces_expose_package_cli_and_mcp() -> None:
    payload = module.complaint_manager_interfaces()

    assert payload["package"]["module"] == "complaint_generator"
    assert payload["package"]["service_class"] == "ComplaintWorkspaceService"
    assert payload["package"]["mcp_handler_module"] == "complaint_generator.mcp"
    assert payload["package"]["workspace_module"] == "complaint_generator.workspace"
    assert "generate_complaint" in payload["package"]["workspace_helpers"]
    assert payload["cli"]["module"] == "complaint_generator.cli"
    assert payload["cli"]["module_entrypoint"] == "complaint_generator.cli:main"
    assert payload["cli"]["module_command"] == "python -m complaint_generator.cli --help"
    assert payload["cli"]["script_name"] == "complaint-workspace"
    assert payload["mcp"]["module"] == "complaint_generator.mcp_server"
    assert payload["mcp"]["module_entrypoint"] == "complaint_generator.mcp_server:main"
    assert payload["mcp"]["module_command"] == "python -m complaint_generator.mcp_server"
    assert payload["mcp"]["protocol_module"] == "complaint_generator.mcp"
    assert payload["mcp"]["script_name"] == "complaint-mcp-server"
    assert payload["mcp"]["launcher_alias"] == "complaint-generator-mcp"
