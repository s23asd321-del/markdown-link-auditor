from __future__ import annotations

import json

import pytest

from markdown_link_auditor.cli import main


def test_cli_json_output_and_exit_code(tmp_path, capsys):
    (tmp_path / "README.md").write_text("[Missing](missing.md)\n", encoding="utf-8")

    exit_code = main(["check", str(tmp_path), "--format", "json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 1
    assert payload["summary"]["errors"] == 1
    assert payload["issues"][0]["rule"] == "missing-file"


def test_cli_strict_fails_on_warning(tmp_path, capsys):
    (tmp_path / "README.md").write_text("# Same\n# Same\n", encoding="utf-8")

    exit_code = main(["check", str(tmp_path), "--strict"])

    assert exit_code == 1
    assert "duplicate-heading" in capsys.readouterr().out


def test_cli_output_does_not_overwrite_without_force(tmp_path, capsys):
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")
    report = tmp_path / "report.md"
    report.write_text("existing report\n", encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        main(["check", str(tmp_path / "README.md"), "--output", str(report)])

    captured = capsys.readouterr()
    assert exc_info.value.code == 2
    assert "already exists" in captured.err
    assert report.read_text(encoding="utf-8") == "existing report\n"


def test_cli_output_overwrites_with_force(tmp_path):
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")
    report = tmp_path / "report.md"
    report.write_text("existing report\n", encoding="utf-8")

    exit_code = main(
        ["check", str(tmp_path / "README.md"), "--output", str(report), "--force"]
    )

    assert exit_code == 0
    assert "markdown-link-auditor report" in report.read_text(encoding="utf-8")
