"""Small Markdown parser for the auditor's local checks."""

from __future__ import annotations

import re
from pathlib import Path

from .anchors import assign_unique_anchor, slugify_heading
from .models import Document, Heading, Issue, Link


HEADING_RE = re.compile(r"^(?P<indent> {0,3})(?P<marks>#{1,6})[ \t]+(?P<text>.+?)\s*$")
REFERENCE_DEFINITION_RE = re.compile(r"^ {0,3}\[([^\]]+)\]:[ \t]*(.*)$")
INLINE_LINK_RE = re.compile(r"(!)?\[([^\]\n]*)\]\(([^)\n]*)\)")
REFERENCE_LINK_RE = re.compile(r"(?<!!)\[([^\]\n]+)\]\[([^\]\n]*)\]")
FENCE_START_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def parse_document(path: Path, text: str) -> Document:
    """Parse the Markdown features needed by the first version."""

    document = Document(path=path, text_lines=text.splitlines())
    reference_definitions: dict[str, tuple[int, int, str]] = {}
    reference_uses: list[tuple[int, int, str]] = []
    seen_anchors: dict[str, int] = {}
    base_anchor_lines: dict[str, int] = {}
    in_fence = False
    fence_marker = ""

    for line_number, line in enumerate(document.text_lines, start=1):
        fence_match = FENCE_START_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            marker_prefix = marker[0]
            marker_length = len(marker)
            if not in_fence:
                in_fence = True
                fence_marker = marker_prefix * marker_length
            elif marker_prefix == fence_marker[0] and marker_length >= len(fence_marker):
                in_fence = False
                fence_marker = ""
            continue

        if in_fence:
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            heading_text = _clean_heading_text(heading_match.group("text"))
            base_anchor = slugify_heading(heading_text)
            anchor = assign_unique_anchor(base_anchor, seen_anchors)
            document.headings.append(
                Heading(text=heading_text, anchor=anchor, path=path, line=line_number)
            )
            if base_anchor in base_anchor_lines:
                document.warnings.append(
                    Issue(
                        severity="warning",
                        code="duplicate-heading",
                        path=path,
                        line=line_number,
                        column=1,
                        summary=(
                            "Heading may collide with an earlier generated anchor "
                            f"from line {base_anchor_lines[base_anchor]}."
                        ),
                        value=heading_text,
                    )
                )
            else:
                base_anchor_lines[base_anchor] = line_number

        definition_match = REFERENCE_DEFINITION_RE.match(line)
        if definition_match:
            identifier = normalize_reference_id(definition_match.group(1))
            target = extract_target_token(definition_match.group(2))
            column = line.find("]:") + 3
            reference_definitions[identifier] = (line_number, max(column, 1), target)
            document.links.append(
                Link(
                    kind="reference-definition",
                    path=path,
                    line=line_number,
                    column=max(column, 1),
                    raw_target=target,
                    label=identifier,
                )
            )
            continue

        for match in INLINE_LINK_RE.finditer(line):
            raw_target = extract_target_token(match.group(3))
            document.links.append(
                Link(
                    kind="image" if match.group(1) else "link",
                    path=path,
                    line=line_number,
                    column=match.start() + 1,
                    raw_target=raw_target,
                    label=match.group(2),
                )
            )

        for match in REFERENCE_LINK_RE.finditer(line):
            label = normalize_reference_id(match.group(2) or match.group(1))
            reference_uses.append((line_number, match.start() + 1, label))

    for line_number, column, label in reference_uses:
        if label not in reference_definitions:
            document.warnings.append(
                Issue(
                    severity="error",
                    code="undefined-reference",
                    path=path,
                    line=line_number,
                    column=column,
                    summary="Reference-style link has no matching definition.",
                    value=label,
                )
            )
    return document


def normalize_reference_id(value: str) -> str:
    """Normalize a reference-style link label."""

    return " ".join(value.strip().lower().split())


def extract_target_token(raw_value: str) -> str:
    """Extract the destination token from a Markdown link target."""

    value = raw_value.strip()
    if not value:
        return ""
    if value.startswith("<"):
        end = value.find(">")
        if end != -1:
            return value[1:end].strip()
    if value[0] in {"'", '"'}:
        return value.strip(value[0])
    return value.split()[0].strip()


def _clean_heading_text(text: str) -> str:
    text = text.strip()
    if text.endswith("#"):
        text = re.sub(r"[ \t]+#+[ \t]*$", "", text)
    return text.strip()
