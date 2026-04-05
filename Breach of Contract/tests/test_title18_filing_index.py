from formal_logic.title18_filing_index import build_title18_filing_index, build_title18_proposed_orders, render_proposed_order_markdown, render_title18_filing_index_markdown


def test_title18_proposed_orders_cover_hacc_and_quantum_paths():
    orders = build_title18_proposed_orders()

    assert orders["meta"]["packetId"] == "title18_proposed_orders_001"
    assert orders["orders"]["hacc"]["sourceMotionId"] == "title18_hacc_party_motion_001"
    assert orders["orders"]["quantum"]["sourceMotionId"] == "title18_quantum_party_motion_001"


def test_title18_filing_index_tracks_artifacts_and_placeholder_work():
    index = build_title18_filing_index()
    hacc_order_markdown = render_proposed_order_markdown(build_title18_proposed_orders()["orders"]["hacc"])
    index_markdown = render_title18_filing_index_markdown(index)

    assert any(item["label"] == "HACC proposed order" for item in index["artifacts"])
    assert "[CASE NUMBER]" in index["unresolvedPlaceholdersByDocument"]["merged_motion"]
    assert "Proposed Order Staying or Denying Displacement Relief" in hacc_order_markdown
    assert "# Title 18 Filing Index" in index_markdown