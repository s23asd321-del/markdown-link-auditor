from __future__ import annotations

import json

from markdown_link_auditor import audit_path
from markdown_link_auditor.reporters import render_json, render_text


def test_local_paths_are_redacted_in_default_reports(tmp_path):
    (tmp_path / "README.md").write_text("Fake path: /Users/demo/private/path\n", encoding="utf-8")
    result = audit_path(tmp_path)

    text = render_text(result)
    payload = json.loads(render_json(result))

    assert "/Users/demo" not in text
    assert payload["issues"][0]["value"] == "redacted local path"


def test_no_values_hides_non_sensitive_targets_too(tmp_path):
    (tmp_path / "README.md").write_text("[Missing](missing.md)\n", encoding="utf-8")
    result = audit_path(tmp_path)

    payload = json.loads(render_json(result, no_values=True))

    assert "value" not in payload["issues"][0]
