from __future__ import annotations

from markdown_link_auditor.anchors import assign_unique_anchor, slugify_heading


def test_slugify_heading_handles_common_markdown_formatting():
    assert slugify_heading("Using `check` With [Docs](docs.md)!") == "using-check-with-docs"


def test_assign_unique_anchor_adds_github_style_suffixes():
    seen: dict[str, int] = {}

    assert assign_unique_anchor("usage", seen) == "usage"
    assert assign_unique_anchor("usage", seen) == "usage-1"
    assert assign_unique_anchor("usage", seen) == "usage-2"
