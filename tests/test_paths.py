from __future__ import annotations

from markdown_link_auditor import audit_path


def test_project_ignore_file_skips_patterns_when_scanning_directory(tmp_path):
    (tmp_path / ".markdown-link-auditor-ignore").write_text("bad-docs/\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")
    bad_docs = tmp_path / "bad-docs"
    bad_docs.mkdir()
    (bad_docs / "README.md").write_text("[Missing](missing.md)\n", encoding="utf-8")

    root_result = audit_path(tmp_path)
    direct_result = audit_path(bad_docs)

    assert root_result.error_count == 0
    assert direct_result.error_count == 1


def test_hidden_directories_are_skipped_by_default(tmp_path):
    hidden = tmp_path / ".drafts"
    hidden.mkdir()
    (hidden / "README.md").write_text("[missing](missing.md)\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")

    result = audit_path(tmp_path)

    assert result.error_count == 0
