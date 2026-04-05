from formal_logic.title18_filing_draft import build_title18_filing_draft, render_title18_filing_draft_markdown
from formal_logic.title18_motion_support import build_motion_support_packet, render_motion_support_markdown
from formal_logic.title18_query import available_presets, run_preset, load_report


def test_title18_query_presets_cover_expected_views():
    report = load_report()
    assert "hacc-overdue" in available_presets()
    payload = run_preset(report, "hacc-overdue")
    assert payload["summary"]["count"] >= 1
    assert payload["summary"]["byActor"]["org:hacc"] >= 1


def test_title18_motion_support_packet_contains_sections_and_exhibit_map():
    packet = build_motion_support_packet()
    markdown = render_motion_support_markdown(packet)
    assert packet["meta"]["packetId"] == "title18_motion_support_001"
    assert packet["sections"]
    assert packet["exhibitMap"]
    assert "# Title 18 Motion Support Packet" in markdown


def test_title18_filing_draft_contains_sections_and_reference_sources():
    draft = build_title18_filing_draft()
    markdown = render_title18_filing_draft_markdown(draft)
    assert draft["meta"]["draftId"] == "title18_filing_draft_001"
    assert draft["sections"]
    assert draft["referenceDrafts"]["emergencyMotion"]
    assert "# Title 18 Filing Draft" in markdown