from formal_logic.title18_readiness import build_title18_readiness_report, render_title18_readiness_markdown


def test_title18_readiness_report_tracks_hacc_and_quantum_status():
    report = build_title18_readiness_report()

    assert report["meta"]["reportId"] == "title18_readiness_report_001"
    assert "hacc" in report["tracks"]
    assert "quantum" in report["tracks"]
    assert report["tracks"]["hacc"]["missingCount"] >= 1


def test_title18_readiness_markdown_renders_heading():
    markdown = render_title18_readiness_markdown(build_title18_readiness_report())

    assert "# Title 18 Readiness Report" in markdown