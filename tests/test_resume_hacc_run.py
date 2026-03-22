from pathlib import Path
from subprocess import CompletedProcess
import os
from unittest import mock

import resume_hacc_run as module


def test_main_resumes_latest_grounded_run(tmp_path, capsys):
    older = tmp_path / "older"
    newer = tmp_path / "newer"
    older.mkdir()
    newer.mkdir()
    os.utime(older, (1, 1))
    os.utime(newer, (2, 2))

    calls = []

    def fake_run(cmd, cwd=None, check=False):
        calls.append((cmd, cwd, check))
        return CompletedProcess(cmd, 0)

    with (
        mock.patch.object(module, "GROUNDED_RUNS_DIR", tmp_path),
        mock.patch.object(module.subprocess, "run", side_effect=fake_run),
    ):
        exit_code = module.main(["grounded", "--latest", "--", "--synthesize-complaint"])

    assert exit_code == 0
    assert len(calls) == 1
    cmd = calls[0][0]
    assert cmd[1].endswith("hacc_grounded_pipeline.py")
    assert "--reuse-existing-artifacts" in cmd
    assert "--synthesize-complaint" in cmd
    assert str(newer.resolve()) in cmd
    output = capsys.readouterr().out
    assert f"Resuming grounded run: {newer.resolve()}" in output


def test_main_resumes_explicit_adversarial_run(tmp_path, capsys):
    run_dir = tmp_path / "adv"
    run_dir.mkdir()
    calls = []

    def fake_run(cmd, cwd=None, check=False):
        calls.append((cmd, cwd, check))
        return CompletedProcess(cmd, 0)

    with mock.patch.object(module.subprocess, "run", side_effect=fake_run):
        exit_code = module.main(["adversarial", str(run_dir), "--", "--hacc-search-mode", "lexical"])

    assert exit_code == 0
    assert len(calls) == 1
    cmd = calls[0][0]
    assert cmd[1].endswith("hacc_adversarial_runner.py")
    assert "--reuse-existing-artifacts" in cmd
    assert "--hacc-search-mode" in cmd
    assert "lexical" in cmd
    assert str(run_dir.resolve()) in cmd
    output = capsys.readouterr().out
    assert f"Resuming adversarial run: {run_dir.resolve()}" in output


def test_main_requires_path_or_latest():
    try:
        module.main(["grounded"])
    except FileNotFoundError as exc:
        assert str(exc) == "Either provide a run directory or use --latest."
    else:
        raise AssertionError("expected FileNotFoundError when no run source is provided")
