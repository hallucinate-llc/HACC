from formal_logic.title18_party_drafts import build_hacc_party_motion, build_quantum_party_motion, render_party_motion_markdown


def test_title18_party_drafts_split_hacc_and_quantum_tracks():
    hacc = build_hacc_party_motion()
    quantum = build_quantum_party_motion()

    assert hacc["meta"]["draftId"] == "title18_hacc_party_motion_001"
    assert quantum["meta"]["draftId"] == "title18_quantum_party_motion_001"
    assert any(section["id"] == "hacc_core_failures" for section in hacc["sections"])
    assert any(section["id"] == "quantum_core_theories" for section in quantum["sections"])


def test_title18_party_draft_markdown_includes_party_specific_titles():
    hacc_markdown = render_party_motion_markdown(build_hacc_party_motion())
    quantum_markdown = render_party_motion_markdown(build_quantum_party_motion())

    assert "HACC-FOCUSED MOTION" in hacc_markdown
    assert "QUANTUM-FOCUSED MOTION" in quantum_markdown