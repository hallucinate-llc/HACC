#!/usr/bin/env python3
"""Render dependency graph and JSON-LD citations for the joinder eviction-defense case.

Usage
-----
    python render_joinder_graph.py <fixture.json> [--write]

With --write, outputs are written to outputs/joinder_quantum_001_dependency_graph.json
and outputs/joinder_quantum_001_dependency_citations.jsonld.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Allow running from repo root without installing the package
sys.path.insert(0, str(ROOT))

from engine.joinder_grounding import (  # noqa: E402
    build_dependency_citations_jsonld,
    dependency_graph_payload,
)


def main(argv: list) -> int:
    if len(argv) not in {2, 3}:
        print(
            "usage: render_joinder_graph.py <fixture.json> [--write]",
            file=sys.stderr,
        )
        return 2

    write_output = len(argv) == 3 and argv[2] == "--write"
    if len(argv) == 3 and not write_output:
        print(
            "usage: render_joinder_graph.py <fixture.json> [--write]",
            file=sys.stderr,
        )
        return 2

    fixture_path = Path(argv[1])
    if not fixture_path.exists():
        print(f"error: fixture not found: {fixture_path}", file=sys.stderr)
        return 1

    case_payload = json.loads(fixture_path.read_text())

    graph = dependency_graph_payload(case_payload)
    citations = build_dependency_citations_jsonld(case_payload)

    case_id = case_payload.get("caseId", "joinder_quantum_001")

    print("=== Dependency Graph ===")
    print(json.dumps(graph, indent=2))
    print()
    print("=== Dependency Citations (JSON-LD) — @graph node count:", len(citations["@graph"]), "===")

    if write_output:
        output_dir = ROOT / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        graph_path = output_dir / f"{case_id}_dependency_graph.json"
        citations_path = output_dir / f"{case_id}_dependency_citations.jsonld"

        def atomic_write(path: Path, text: str) -> None:
            tmp = path.with_name(f".{path.name}.tmp")
            tmp.write_text(text)
            tmp.replace(path)

        atomic_write(graph_path, json.dumps(graph, indent=2) + "\n")
        atomic_write(citations_path, json.dumps(citations, indent=2) + "\n")

        print(f"\nWrote dependency graph  → {graph_path}")
        print(f"Wrote dependency citations → {citations_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
