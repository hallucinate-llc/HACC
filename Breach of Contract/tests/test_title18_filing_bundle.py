import json
from pathlib import Path

from formal_logic.title18_filing_bundle import build_title18_filing_bundle, render_title18_filing_bundle_markdown


def test_title18_filing_bundle_assembles_core_artifacts_and_counts():
    bundle = build_title18_filing_bundle()
    assert bundle["meta"]["bundleId"] == "title18_filing_packet_001"
    assert bundle["summary"]["obligationCount"] >= 10
    assert bundle["summary"]["likelyBreachCount"] >= 1
    assert any(item["label"] == "Breach report" for item in bundle["artifacts"])
    assert bundle["priorityDiscoveryRequests"]


def test_title18_filing_bundle_markdown_surfaces_topline_and_artifacts():
    bundle = build_title18_filing_bundle()
    markdown = render_title18_filing_bundle_markdown(bundle)
    assert "# Title 18 Filing Packet" in markdown
    assert "Likely breach:" in markdown
    assert "Breach report" in markdown