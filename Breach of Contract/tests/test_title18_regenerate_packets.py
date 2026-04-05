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