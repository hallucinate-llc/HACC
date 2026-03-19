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

    def fake_run(cmd, cwd=None, check=False, capture_output=False, text=False):
        calls.append((cmd, cwd, check))
        if cmd[1].endswith("hacc_grounded_pipeline.py"):
            return CompletedProcess(
                cmd,
                0,
                stdout=(
                    "Output directory: /tmp/rerun-output\n"
                    "Draft complaint package: /tmp/rerun-output/complaint_synthesis/draft_complaint_package.json\n"
                    "Intake worksheet: /tmp/rerun-output/complaint_synthesis/intake_follow_up_worksheet.json\n"
                ),
                stderr="",
            )
        return CompletedProcess(cmd, 0, stdout="", stderr="")

    with mock.patch.object(module.subprocess, "run", side_effect=fake_run):
        exit_code = module.main([worksheet, "--", "--demo", "--synthesize-complaint", "--filing-forum", "hud"])

    assert exit_code == 0
    assert len(calls) == 2
    output = capsys.readouterr().out
    assert "Worksheet preflight summary:" in output
    assert f"- grounded_run: {tmp_path}" in output
    assert f"- worksheet: {worksheet}" in output
    assert "- item_count: 3" in output
    assert "- answered: 3" in output
    assert "Output directory: /tmp/rerun-output" in output
    assert "Rerun artifacts: /tmp/rerun-output" in output
    assert "Refreshed complaint draft: /tmp/rerun-output/complaint_synthesis/draft_complaint_package.json" in output
    assert "Refreshed complaint markdown: /tmp/rerun-output/complaint_synthesis/draft_complaint_package.md" in output
    assert "Refreshed intake worksheet: /tmp/rerun-output/complaint_synthesis/intake_follow_up_worksheet.json" in output
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


def test_main_stops_when_validation_fails(tmp_path):
    worksheet_path = tmp_path / "intake_follow_up_worksheet.json"
    worksheet_path.write_text("{}", encoding="utf-8")
    worksheet = str(worksheet_path)

    def fake_run(cmd, cwd=None, check=False, capture_output=False, text=False):
        if cmd[1].endswith("validate_intake_follow_up_worksheet.py"):
            return CompletedProcess(cmd, 2, stdout="", stderr="")
        raise AssertionError("pipeline should not run when validation fails")

    with mock.patch.object(module.subprocess, "run", side_effect=fake_run):
        exit_code = module.main([worksheet, "--", "--demo"])

    assert exit_code == 2


def test_main_accepts_grounded_run_directory_and_discovers_worksheet(tmp_path):
    run_dir = tmp_path / "grounded_run"
    worksheet_path = run_dir / "complaint_synthesis" / "intake_follow_up_worksheet.json"
    worksheet_path.parent.mkdir(parents=True)
    worksheet_path.write_text(
        """
        {
          "validation_summary": {
            "item_count": 2,
            "status_counts": {"answered": 2},
            "all_answered": true,
            "open_question_count": 0,
            "invalid_question_count": 0
          }
        }
        """.strip(),
        encoding="utf-8",
    )
    calls = []

    def fake_run(cmd, cwd=None, check=False, capture_output=False, text=False):
        calls.append((cmd, cwd, check))
        if cmd[1].endswith("hacc_grounded_pipeline.py"):
            return CompletedProcess(
                cmd,
                0,
                stdout=(
                    "Output directory: /tmp/grounded-run-output\n"
                    "Draft complaint package: /tmp/grounded-run-output/complaint_synthesis/draft_complaint_package.json\n"
                ),
                stderr="",
            )
        return CompletedProcess(cmd, 0, stdout="", stderr="")

    with mock.patch.object(module.subprocess, "run", side_effect=fake_run):
        exit_code = module.main([str(run_dir), "--", "--demo"])

    assert exit_code == 0
    assert len(calls) == 2
    validator_cmd = calls[0][0]
    pipeline_cmd = calls[1][0]
    assert str(worksheet_path.resolve()) in validator_cmd
    assert str(worksheet_path.resolve()) in pipeline_cmd


def test_main_accepts_latest_and_uses_newest_grounded_run(tmp_path, capsys):
    older_run = tmp_path / "older_run"
    newer_run = tmp_path / "newer_run"
    older_worksheet = older_run / "complaint_synthesis" / "intake_follow_up_worksheet.json"
    newer_worksheet = newer_run / "complaint_synthesis" / "intake_follow_up_worksheet.json"
    older_worksheet.parent.mkdir(parents=True)
    newer_worksheet.parent.mkdir(parents=True)
    older_worksheet.write_text(
        '{"validation_summary":{"item_count":1,"status_counts":{"answered":1},"all_answered":true,"open_question_count":0,"invalid_question_count":0}}',
        encoding="utf-8",
    )
    newer_worksheet.write_text(
        '{"validation_summary":{"item_count":4,"status_counts":{"answered":4},"all_answered":true,"open_question_count":0,"invalid_question_count":0}}',
        encoding="utf-8",
    )
    older_run.touch()
    newer_run.touch()
    calls = []

    def fake_run(cmd, cwd=None, check=False, capture_output=False, text=False):
        calls.append((cmd, cwd, check))
        if cmd[1].endswith("hacc_grounded_pipeline.py"):
            return CompletedProcess(
                cmd,
                0,
                stdout=(
                    "Output directory: /tmp/latest-rerun-output\n"
                    "Draft complaint package: /tmp/latest-rerun-output/complaint_synthesis/draft_complaint_package.json\n"
                ),
                stderr="",
            )
        return CompletedProcess(cmd, 0, stdout="", stderr="")

    with (
        mock.patch.object(module, "GROUNDED_RUNS_DIR", tmp_path),
        mock.patch.object(module.subprocess, "run", side_effect=fake_run),
    ):
        exit_code = module.main(["--latest", "--", "--demo", "--filing-forum", "hud"])

    assert exit_code == 0
    assert len(calls) == 2
    output = capsys.readouterr().out
    assert f"- grounded_run: {newer_run.resolve()}" in output
    assert f"- worksheet: {newer_worksheet.resolve()}" in output
    assert "Refreshed complaint draft: /tmp/latest-rerun-output/complaint_synthesis/draft_complaint_package.json" in output
    assert "Refreshed complaint markdown: /tmp/latest-rerun-output/complaint_synthesis/draft_complaint_package.md" in output
    validator_cmd = calls[0][0]
    pipeline_cmd = calls[1][0]
    assert str(newer_worksheet.resolve()) in validator_cmd
    assert str(newer_worksheet.resolve()) in pipeline_cmd


def test_main_requires_path_or_latest():
    try:
        module.main([])
    except SystemExit as exc:
        assert str(exc) == "Either provide a worksheet path/run directory or use --latest."
    else:
        raise AssertionError("expected SystemExit when no worksheet source is provided")
