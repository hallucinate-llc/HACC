import json
from pathlib import Path

import show_grounded_artifacts as module


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload))


def test_main_prints_human_readable_summary(tmp_path, capsys):
    run_dir = tmp_path / "grounded-run"
    _write_json(
        run_dir / "synthetic_prompts.json",
        {
            "evidence_upload_prompts": [
                {
                    "title": "Policy A",
                    "relative_path": "repo/policy-a.txt",
                    "anchor_sections": ["grievance_hearing"],
                }
            ],
            "mediator_questions": ["What record proves the hearing date?"],
            "blocker_objectives": ["exact_dates"],
            "production_evidence_intake_steps": ["Upload the strongest notices first."],
            "mediator_upload_checklist": ["Identify what exact fact each uploaded file proves."],
        },
    )
    _write_json(
        run_dir / "grounding_bundle.json",
        {
            "query": "housing retaliation grievance",
            "claim_type": "housing_discrimination",
            "upload_candidates": [
                {
                    "title": "Policy A",
                    "snippet": "Strong notice language",
                    "metadata": {"selection_priority": 11.5},
                }
            ],
        },
    )
    _write_json(
        run_dir / "external_research_bundle.json",
        {
            "query": "housing retaliation grievance",
            "claim_type": "housing_discrimination",
            "summary": {
                "web_result_count": 2,
                "legal_result_count": 1,
                "top_web_titles": ["24 CFR Part 966"],
                "top_legal_titles": ["Fair Housing Act retaliation"],
            },
        },
    )
    _write_json(
        run_dir / "complaint_synthesis" / "draft_complaint_package.json",
        {
            "evidence_attachments": [
                {
                    "title": "Policy A",
                    "uploaded_to_mediator": True,
                    "relative_path": "repo/policy-a.txt",
                }
            ],
            "authorities_and_research_basis": {
                "authority_records": [
                    {
                        "type": "Regulation",
                        "label": "24 CFR Part 966",
                        "why_it_matters": "supports grievance allegations",
                        "url": "https://example.test/966",
                    }
                ],
                "corroborating_web_research_records": [],
            },
        },
    )
    _write_json(run_dir / "run_summary.json", {"status": "completed"})
    _write_json(run_dir / "progress.json", {"stage": "completed"})

    exit_code = module.main([str(run_dir)])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Grounded run:" in output
    assert "Upload Prompts" in output
    assert "Top Evidence Candidates" in output
    assert "Authorities" in output
    assert "24 CFR Part 966" in output
    assert "Mediator Questions" in output
    assert "exact_dates" in output


def test_main_prints_json_summary(tmp_path, capsys):
    run_dir = tmp_path / "grounded-run"
    _write_json(run_dir / "synthetic_prompts.json", {"evidence_upload_prompts": []})
    _write_json(run_dir / "grounding_bundle.json", {"query": "q", "claim_type": "c", "upload_candidates": []})
    _write_json(run_dir / "external_research_bundle.json", {"summary": {}})
    _write_json(
        run_dir / "complaint_synthesis" / "draft_complaint_package.json",
        {"authorities_and_research_basis": {}},
    )

    exit_code = module.main([str(run_dir), "--json"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["query"] == "q"
    assert payload["claim_type"] == "c"


def test_main_can_filter_sections(tmp_path, capsys):
    run_dir = tmp_path / "grounded-run"
    _write_json(
        run_dir / "synthetic_prompts.json",
        {
            "evidence_upload_prompts": [
                {"title": "Policy A", "relative_path": "repo/policy-a.txt", "anchor_sections": []}
            ],
            "mediator_questions": ["Which record proves the date?"],
        },
    )
    _write_json(run_dir / "grounding_bundle.json", {"query": "q", "claim_type": "c", "upload_candidates": []})
    _write_json(run_dir / "external_research_bundle.json", {"summary": {}})
    _write_json(
        run_dir / "complaint_synthesis" / "draft_complaint_package.json",
        {"authorities_and_research_basis": {}, "evidence_attachments": []},
    )

    exit_code = module.main([str(run_dir), "--section", "mediator-questions"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Mediator Questions" in output
    assert "Which record proves the date?" in output
    assert "Upload Prompts" not in output


def test_main_can_write_brief(tmp_path, capsys):
    run_dir = tmp_path / "grounded-run"
    _write_json(
        run_dir / "synthetic_prompts.json",
        {
            "evidence_upload_prompts": [
                {"title": "Policy A", "relative_path": "repo/policy-a.txt", "anchor_sections": []}
            ],
            "mediator_questions": ["Which record proves the date?"],
            "blocker_objectives": ["exact_dates"],
        },
    )
    _write_json(
        run_dir / "grounding_bundle.json",
        {"query": "q", "claim_type": "c", "upload_candidates": [{"title": "Policy A", "snippet": "notice", "metadata": {}}]},
    )
    _write_json(
        run_dir / "external_research_bundle.json",
        {"summary": {"web_result_count": 1, "legal_result_count": 0, "top_web_titles": [], "top_legal_titles": []}},
    )
    _write_json(
        run_dir / "complaint_synthesis" / "draft_complaint_package.json",
        {
            "evidence_attachments": [],
            "authorities_and_research_basis": {
                "authority_records": [
                    {
                        "type": "Regulation",
                        "label": "24 CFR Part 966",
                        "why_it_matters": "supports grievance allegations",
                        "url": "https://example.test/966",
                    }
                ]
            },
        },
    )

    exit_code = module.main([str(run_dir), "--write-brief"])

    assert exit_code == 0
    output = capsys.readouterr().out
    brief_path = run_dir / "grounded_run_brief.md"
    assert f"Wrote brief: {brief_path}" in output
    brief_text = brief_path.read_text()
    assert "# Grounded Run Brief" in brief_text
    assert "## Mediator Questions" in brief_text
    assert "24 CFR Part 966" in brief_text


def test_main_requires_path_or_latest():
    try:
        module.main([])
    except FileNotFoundError as exc:
        assert str(exc) == "Either provide a grounded run directory or use --latest."
    else:
        raise AssertionError("expected FileNotFoundError when no run source is provided")
