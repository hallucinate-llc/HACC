from formal_logic.title18_override_templates import (
    _merge_template_into_editable,
    build_title18_override_templates,
    render_title18_override_worksheet_markdown,
)


def test_title18_override_templates_split_hacc_and_quantum_missing_fields():
    bundle = build_title18_override_templates()

    assert bundle["meta"]["templateId"] == "title18_override_templates_001"
    assert bundle["meta"]["editableOverridePaths"]["hacc"].endswith("title18_hacc_context_overrides.json")
    assert bundle["completion"]["hacc"]["totalCount"] >= 1
    assert "[CASE NUMBER]" in bundle["templates"]["hacc"]["requiredUserInputs"]
    assert "[FULL LEGAL ENTITY NAME]" in bundle["templates"]["quantum"]["requiredUserInputs"]


def test_title18_override_worksheet_markdown_renders_heading():
    markdown = render_title18_override_worksheet_markdown(build_title18_override_templates())

    assert "# Title 18 Override Worksheet" in markdown
    assert "Editable HACC override file" in markdown
    assert "Filled fields:" in markdown


def test_merge_template_into_editable_preserves_existing_values_and_adds_new_keys():
    existing = {
        "substitutions": {"[CASE NUMBER]": "26CV12345"},
        "requiredUserInputs": {"[NAME]": "Benjamin Barber"},
    }
    template = {
        "substitutions": {"[CASE NUMBER]": None, "[DATE]": None},
        "requiredUserInputs": {"[NAME]": None, "[EMAIL]": None},
    }

    merged = _merge_template_into_editable(existing, template)

    assert merged["substitutions"]["[CASE NUMBER]"] == "26CV12345"
    assert merged["substitutions"]["[DATE]"] is None
    assert merged["requiredUserInputs"]["[NAME]"] == "Benjamin Barber"
    assert merged["requiredUserInputs"]["[EMAIL]"] is None