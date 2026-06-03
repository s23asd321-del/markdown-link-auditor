from __future__ import annotations

from markdown_link_auditor import audit_path


def codes(result):
    return [issue.code for issue in result.issues]


def test_local_file_image_and_anchor_rules(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "overview.md").write_text("# Overview\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "\n".join(
            [
                "# Project",
                "[Missing](missing.md)",
                "![Image](missing.png)",
                "[Bad anchor](docs/overview.md#missing)",
                "[Empty]()",
            ]
        ),
        encoding="utf-8",
    )

    result = audit_path(tmp_path)

    assert codes(result) == ["missing-file", "missing-image", "missing-anchor", "empty-link"]


def test_warning_rules_for_duplicate_todo_file_url_and_unsupported_scheme(tmp_path):
    (tmp_path / "README.md").write_text(
        "\n".join(
            [
                "# Project",
                "# Project",
                "[Todo](TODO)",
                "[Unsupported](ftp://example.invalid/demo)",
                "Fake path: /Users/demo/private/path",
                "Fake URL: file:///Users/demo/secret.txt",
            ]
        ),
        encoding="utf-8",
    )

    result = audit_path(tmp_path)

    assert codes(result) == [
        "duplicate-heading",
        "todo-link",
        "unsupported-scheme",
        "local-absolute-path",
        "local-file-url",
    ]
