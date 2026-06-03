from __future__ import annotations

import json

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
