from __future__ import annotations

import json

from markdown_link_auditor import AuditConfig, audit_path
from markdown_link_auditor.cli import main
from markdown_link_auditor.reporters import render_json, render_text


def issue_codes(result):
    return [issue.code for issue in result.issues]


def test_reports_missing_local_files_and_images(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Project",
                "[missing doc](docs/missing.md)",
                "![missing image](assets/logo.png)",
            ]
        ),
        encoding="utf-8",
    )

    result = audit_path(tmp_path)

    assert issue_codes(result) == ["missing-file", "missing-image"]
    assert result.error_count == 2


def test_checks_same_file_and_cross_file_anchors(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("# Usage\n\n# Usage\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "\n".join(
            [
                "# Intro",
                "[same-file ok](#intro)",
                "[same-file missing](#does-not-exist)",
                "[cross-file ok](docs/guide.md#usage)",
                "[cross-file duplicate ok](docs/guide.md#usage-1)",
                "[cross-file missing](docs/guide.md#missing)",
            ]
        ),
        encoding="utf-8",
    )

    result = audit_path(tmp_path)

    assert issue_codes(result) == [
        "missing-anchor",
        "missing-anchor",
        "duplicate-heading",
    ]
    assert result.error_count == 2
    assert result.warning_count == 1


def test_skips_links_inside_fenced_code_blocks(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Project",
                "```text",
                "[ignored](missing-inside-code.md)",
                "```",
                "[checked](missing-outside-code.md)",
            ]
        ),
        encoding="utf-8",
    )

    result = audit_path(readme)

    assert issue_codes(result) == ["missing-file"]
    assert result.issues[0].value == "missing-outside-code.md"


def test_reference_style_links_and_empty_definitions(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("# Usage\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "\n".join(
            [
                "# Project",
                "[ok][guide]",
                "[bad][missing]",
                "",
                "[guide]: docs/guide.md#usage",
                "[empty]:",
            ]
        ),
        encoding="utf-8",
    )

    result = audit_path(tmp_path)

    assert issue_codes(result) == ["undefined-reference", "empty-link"]
    assert result.error_count == 2


def test_sensitive_local_values_are_redacted_in_reports(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(
        "# Project\nThis mentions /Users/alice/private-note.md outside a code block.\n",
        encoding="utf-8",
    )

    result = audit_path(readme)
    text_report = render_text(result)
    json_report = render_json(result)

    assert issue_codes(result) == ["local-absolute-path"]
    assert "/Users/alice" not in text_report
    assert "/Users/alice" not in json_report
    assert "[redacted local path]" in text_report


def test_no_values_hides_all_values(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Project\n[missing](missing.md)\n", encoding="utf-8")

    result = audit_path(readme)
    payload = json.loads(render_json(result, no_values=True))

    assert payload["issues"][0]["rule"] == "missing-file"
    assert "value" not in payload["issues"][0]


def test_cli_json_output_and_exit_code(tmp_path, capsys):
    (tmp_path / "README.md").write_text("# Project\n[missing](missing.md)\n", encoding="utf-8")

    exit_code = main(["check", str(tmp_path), "--format", "json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 1
    assert payload["summary"]["errors"] == 1
    assert payload["issues"][0]["rule"] == "missing-file"


def test_hidden_directories_are_skipped_by_default(tmp_path):
    hidden = tmp_path / ".drafts"
    hidden.mkdir()
    (hidden / "README.md").write_text("[missing](missing.md)\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")

    default_result = audit_path(tmp_path)
    hidden_result = audit_path(tmp_path, AuditConfig(include_hidden=True))

    assert default_result.error_count == 0
    assert hidden_result.error_count == 1
