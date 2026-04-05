from formal_logic.title18_merged_motion import build_title18_merged_motion, render_title18_merged_motion_markdown


def test_title18_merged_motion_contains_core_sections_and_order():
    motion = build_title18_merged_motion()
    markdown = render_title18_merged_motion_markdown(motion)
    section_ids = [item["id"] for item in motion["sections"]]

    assert motion["meta"]["motionId"] == "title18_merged_motion_001"
    assert "requested_relief" in section_ids
    assert "proposed_order" in section_ids
    assert motion["exhibitMap"]
    assert "# Title 18 Merged Motion Package" in markdown