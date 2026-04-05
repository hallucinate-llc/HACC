from formal_logic.title18_override_templates import build_title18_override_templates, render_title18_override_worksheet_markdown


def test_title18_override_templates_split_hacc_and_quantum_missing_fields():
    bundle = build_title18_override_templates()

    assert bundle["meta"]["templateId"] == "title18_override_templates_001"
    assert "[CASE NUMBER]" in bundle["templates"]["hacc"]["requiredUserInputs"]
    assert "[FULL LEGAL ENTITY NAME]" in bundle["templates"]["quantum"]["requiredUserInputs"]


def test_title18_override_worksheet_markdown_renders_heading():
    markdown = render_title18_override_worksheet_markdown(build_title18_override_templates())

    assert "# Title 18 Override Worksheet" in markdown