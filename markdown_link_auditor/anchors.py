"""Heading anchor helpers."""

from __future__ import annotations

import html
import re


INLINE_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\([^)]+\)")
INLINE_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
REFERENCE_LINK_RE = re.compile(r"\[([^\]]+)\]\[[^\]]*\]")
HTML_TAG_RE = re.compile(r"<[^>]+>")
PUNCTUATION_RE = re.compile(r"[^\w\s-]", re.UNICODE)
WHITESPACE_RE = re.compile(r"\s+")
HYPHEN_RE = re.compile(r"-+")


def slugify_heading(text: str) -> str:
    """Return a GitHub-like heading slug for common Markdown headings."""

    text = html.unescape(text.strip())
    text = INLINE_IMAGE_RE.sub(r"\1", text)
    text = INLINE_LINK_RE.sub(r"\1", text)
    text = REFERENCE_LINK_RE.sub(r"\1", text)
    text = HTML_TAG_RE.sub("", text)
    text = text.replace("`", "")
    text = text.replace("*", "")
    text = text.replace("_", "")
    text = text.lower()
    text = PUNCTUATION_RE.sub("", text)
    text = WHITESPACE_RE.sub("-", text.strip())
    return HYPHEN_RE.sub("-", text).strip("-")


def assign_unique_anchor(base_anchor: str, seen: dict[str, int]) -> str:
    """Assign GitHub-style duplicate suffixes for a heading anchor."""

    count = seen.get(base_anchor, 0)
    seen[base_anchor] = count + 1
    if count == 0:
        return base_anchor
    return f"{base_anchor}-{count}"
