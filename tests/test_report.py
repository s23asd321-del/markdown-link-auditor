from __future__ import annotations

import json

from markdown_link_auditor import audit_path
from markdown_link_auditor.reporters import render_json, render_markdown, render_text


def test_report_formats_include_summary_and_issues(tmp_path):
    (tmp_path / "README.md").write_text("[Missing](missing.md)\n", encoding="utf-8")
    result = audit_path(tmp_path)

    text = render_text(result)
    markdown = render_markdown(result)
    payload = json.loads(render_json(result))

    assert "Errors: 1" in text
    assert "| README.md | 1 | error | missing-file |" in markdown
    assert payload["summary"]["errors"] == 1
    assert payload["issues"][0]["rule"] == "missing-file"
