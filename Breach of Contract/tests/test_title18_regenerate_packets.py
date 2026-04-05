import json
from pathlib import Path

from formal_logic.title18_regenerate_packets import regenerate_title18_packets
from formal_logic.title18_rendered_filings import build_render_context


def test_title18_render_context_reports_override_path():
    context = build_render_context()

    assert context["meta"]["overridePath"].endswith("title18_render_context_overrides.json")


def test_title18_regenerate_packets_returns_written_paths():
    outputs = regenerate_title18_packets()

    assert isinstance(outputs["rendered_manifest_json"], Path)
    assert outputs["final_quantum_markdown"].name == "title18_quantum_final_packet.md"


def test_title18_regenerate_packets_accepts_quantum_merged_order_track():
    outputs = regenerate_title18_packets(merged_order_track="quantum")

    assert isinstance(outputs["rendered_merged_markdown"], Path)


def test_title18_render_context_layers_multiple_override_files(tmp_path):
    base = tmp_path / "base.json"
    layered = tmp_path / "layered.json"
    base.write_text(
        json.dumps(
            {
                "substitutions": {"[CASE NUMBER]": "26CV00001"},
                "requiredUserInputs": {"[NAME]": "Benjamin Barber"},
            }
        )
    )
    layered.write_text(
        json.dumps(
            {
                "substitutions": {"[CASE NUMBER]": "26CV99999"},
                "requiredUserInputs": {"[EMAIL]": "bb@example.com"},
            }
        )
    )

    context = build_render_context(override_paths=[base, layered])

    assert context["requiredUserInputs"]["[NAME]"] == "Benjamin Barber"
    assert context["requiredUserInputs"]["[EMAIL]"] == "bb@example.com"
    assert context["substitutions"]["[CASE NUMBER]"] == "26CV99999"
    assert context["meta"]["overridePaths"] == [str(base), str(layered)]


def test_title18_regenerate_packets_accepts_override_files(tmp_path):
    override_file = tmp_path / "override.json"
    override_file.write_text(
        json.dumps(
            {
                "substitutions": {},
                "requiredUserInputs": {"[CASE NUMBER]": "26CV12345"},
            }
        )
    )

    regenerate_title18_packets(override_paths=[override_file])
    rendered_context = json.loads(
        (Path("/home/barberb/HACC/Breach of Contract") / "outputs" / "title18_render_context.json").read_text()
    )

    assert rendered_context["requiredUserInputs"]["[CASE NUMBER]"] == "26CV12345"