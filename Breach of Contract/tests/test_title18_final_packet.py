from formal_logic.title18_final_packet import build_title18_final_packet, render_title18_final_packet_markdown


def test_title18_final_packet_builds_hacc_track():
    packet = build_title18_final_packet("hacc")

    assert packet["meta"]["packetId"] == "title18_hacc_final_packet_001"
    assert packet["motion"]["sourceId"] == "title18_hacc_party_motion_001"
    assert packet["proposedOrder"]["orderId"] == "title18_hacc_proposed_order_001"


def test_title18_final_packet_markdown_builds_quantum_packet_sections():
    markdown = render_title18_final_packet_markdown(build_title18_final_packet("quantum"))

    assert "# Title 18 Quantum Final Filing Packet" in markdown
    assert "## Certificate Of Service" in markdown