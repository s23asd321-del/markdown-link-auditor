from __future__ import annotations

from pathlib import Path

from markdown_link_auditor.parser import extract_target_token, normalize_reference_id, parse_document


def test_parser_collects_links_images_references_and_headings():
    document = parse_document(
        Path("README.md"),
        "\n".join(
            [
                "# Intro",
                "[Docs](docs/overview.md)",
                "![Logo](assets/logo.txt)",
                "[Guide][guide]",
                "",
                "[guide]: docs/guide.md#usage",
            ]
        ),
    )

    assert [heading.anchor for heading in document.headings] == ["intro"]
    assert [link.kind for link in document.links] == ["link", "image", "reference-definition"]
    assert document.links[-1].raw_target == "docs/guide.md#usage"


def test_parser_skips_fenced_code_block_links():
    document = parse_document(
        Path("README.md"),
        "\n".join(["# Intro", "```text", "[Skip](missing.md)", "```", "[Keep](ok.md)"]),
    )

    assert [link.raw_target for link in document.links] == ["ok.md"]


def test_reference_helpers_normalize_targets():
    assert normalize_reference_id("  My   Link  ") == "my link"
    assert extract_target_token("<docs/overview.md#usage> optional title") == "docs/overview.md#usage"
