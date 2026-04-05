from formal_logic.title18_service_packet import build_title18_service_packet, render_service_checklist_markdown


def test_title18_service_packet_contains_certificate_and_checklist():
    packet = build_title18_service_packet()

    assert packet["meta"]["packetId"] == "title18_service_packet_001"
    assert "CERTIFICATE OF SERVICE" in packet["certificateOfService"]["markdown"]
    assert "[SERVICE METHOD]" in packet["certificateOfService"]["unresolvedPlaceholders"]


def test_title18_service_checklist_markdown_renders_heading():
    markdown = render_service_checklist_markdown(build_title18_service_packet())

    assert "# Title 18 Filing Service Checklist" in markdown