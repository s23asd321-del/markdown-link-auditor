"""Shared data models for markdown-link-auditor."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Issue:
    """A single audit finding."""

    severity: str
    code: str
    path: Path
    line: int
    column: int
    summary: str
    value: str | None = None
    sensitive: bool = False

    def sort_key(self) -> tuple[str, int, int, str]:
        return (str(self.path), self.line, self.column, self.code)


@dataclass(frozen=True)
class Heading:
    """A Markdown ATX heading and its GitHub-like anchor."""

    text: str
    anchor: str
    path: Path
    line: int


@dataclass(frozen=True)
class Link:
    """A Markdown link target discovered outside fenced code blocks."""

    kind: str
    path: Path
    line: int
    column: int
    raw_target: str
    label: str = ""


@dataclass
class Document:
    """Parsed data from one Markdown document."""

    path: Path
    headings: list[Heading] = field(default_factory=list)
    links: list[Link] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)
    text_lines: list[str] = field(default_factory=list)
