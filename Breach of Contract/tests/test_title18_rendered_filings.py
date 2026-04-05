from formal_logic.title18_rendered_filings import build_render_context, build_rendered_title18_filings


def test_title18_render_context_contains_known_party_values():
    context = build_render_context()

    assert context["substitutions"]["[DATE]"] == "April 5, 2026"
    assert context["substitutions"]["[TENANT FIRST NAMES]"] == "Benjamin Jay Barber and Jane Kay Cortez"
    assert context["requiredUserInputs"]["[CASE NUMBER]"] is None


def test_rendered_title18_filings_report_remaining_placeholders():
    rendered = build_rendered_title18_filings()

    assert "Benjamin Jay Barber and Jane Kay Cortez" in rendered["documents"]["merged_motion"]["renderedMarkdown"]
    assert "April 5, 2026" in rendered["documents"]["quantum_party_motion"]["renderedMarkdown"]
    assert "[CASE NUMBER]" in rendered["documents"]["hacc_party_motion"]["unresolvedPlaceholders"]


def test_rendered_title18_filings_can_switch_merged_order_track():
    rendered = build_rendered_title18_filings(merged_order_track="quantum")

    assert rendered["manifest"]["mergedOrderTrack"] == "quantum"
    assert rendered["documents"]["merged_motion"]["renderedJson"]["meta"]["proposedOrderTrack"] == "quantum"