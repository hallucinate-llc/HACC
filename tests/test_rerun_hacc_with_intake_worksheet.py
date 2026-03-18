from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock

import rerun_hacc_with_intake_worksheet as module


def test_main_validates_then_reruns_pipeline_with_completed_worksheet(tmp_path, capsys):
    worksheet_path = tmp_path / "intake_follow_up_worksheet.json"
    worksheet_path.write_text(
        """
        {
          "validation_summary": {
            "item_count": 3,
            "status_counts": {"answered": 3},
            "all_answered": true,
            "open_question_count": 0,
            "invalid_question_count": 0
          }
        }
        """.strip(),
        encoding="utf-8",
    )
    worksheet = str(worksheet_path)
    calls = []

    def fake_run(cmd, cwd=None, check=False):
        calls.append((cmd, cwd, check))
        return CompletedProcess(cmd, 0)

    with mock.patch.object(module.subprocess, "run", side_effect=fake_run):
        exit_code = module.main([worksheet, "--", "--demo", "--synthesize-complaint", "--filing-forum", "hud"])

    assert exit_code == 0
    assert len(calls) == 2
    output = capsys.readouterr().out
    assert "Worksheet preflight summary:" in output
    assert f"- worksheet: {worksheet}" in output
    assert "- item_count: 3" in output
    assert "- answered: 3" in output
    validator_cmd = calls[0][0]
    pipeline_cmd = calls[1][0]
    assert validator_cmd[1].endswith("validate_intake_follow_up_worksheet.py")
    assert "--require-complete" in validator_cmd
    assert "--in-place" in validator_cmd
    assert pipeline_cmd[1].endswith("hacc_grounded_pipeline.py")
    assert "--completed-intake-worksheet" in pipeline_cmd
    assert "--demo" in pipeline_cmd
    assert "--synthesize-complaint" in pipeline_cmd
    assert "hud" in pipeline_cmd


def test_main_stops_when_validation_fails():
    worksheet = "/tmp/intake_follow_up_worksheet.json"

    def fake_run(cmd, cwd=None, check=False):
        if cmd[1].endswith("validate_intake_follow_up_worksheet.py"):
            return CompletedProcess(cmd, 2)
        raise AssertionError("pipeline should not run when validation fails")

    with mock.patch.object(module.subprocess, "run", side_effect=fake_run):
        exit_code = module.main([worksheet, "--", "--demo"])

    assert exit_code == 2
