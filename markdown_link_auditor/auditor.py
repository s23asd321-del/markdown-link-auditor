"""Core audit engine for local Markdown link checks."""

from __future__ import annotations

import re
from fnmatch import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urlsplit

from .anchors import slugify_heading
from .models import Document, Issue, Link
from .parser import parse_document


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data"}
TODO_TARGETS = {"todo", "tbd", "fixme", "changeme", "placeholder", "your-link-here"}
IGNORE_FILE_NAME = ".markdown-link-auditor-ignore"
LOCAL_FILE_URL_RE = re.compile(r"\bfile://[^\s)\]\"'<>]+", re.IGNORECASE)
POSIX_LOCAL_PATH_RE = re.compile(
    r"(?<![\w:/.-])(?:/Users/|/home/|/private/|/tmp/|/var/)[^\s)\]\"'<>]+"
)
WINDOWS_LOCAL_PATH_RE = re.compile(r"\b[A-Za-z]:\\[^\s)\]\"'<>]+")


class AuditInputError(Exception):
    """Raised when the CLI should report an input/read error."""


@dataclass(frozen=True)
class AuditConfig:
    """Configuration for a local audit run."""

    include_hidden: bool = False
    max_file_size_kb: int = 512
    ignore_file_name: str = IGNORE_FILE_NAME


@dataclass
class AuditResult:
    """Collected documents and findings for one audit run."""

    root: Path
    scanned_files: list[Path] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "warning")


def audit_path(target: Path | str, config: AuditConfig | None = None) -> AuditResult:
    """Audit one Markdown file or a directory of Markdown files."""

    config = config or AuditConfig()
    target_path = Path(target).expanduser()
    if config.max_file_size_kb <= 0:
        raise AuditInputError("--max-file-size-kb must be greater than zero.")
    if not target_path.exists():
        raise AuditInputError(f"Path does not exist: {target_path}")

    resolved_target = target_path.resolve()
    root = resolved_target if resolved_target.is_dir() else resolved_target.parent
    scanned_files = _discover_markdown_files(resolved_target, config)
    result = AuditResult(root=root, scanned_files=scanned_files)
    documents: dict[Path, Document] = {}

    for markdown_file in scanned_files:
        document = _read_document(markdown_file, config, result)
        if document is None:
            continue
        documents[markdown_file] = document
        result.issues.extend(document.warnings)
        result.issues.extend(_find_public_path_warnings(document))

    for document in list(documents.values()):
        for link in document.links:
            result.issues.extend(_check_link(link, document, documents, config, result))

    result.issues.sort(key=lambda issue: issue.sort_key())
    return result


def _discover_markdown_files(target: Path, config: AuditConfig) -> list[Path]:
    if target.is_file():
        if target.suffix.lower() != ".md":
            raise AuditInputError(f"Input file is not a Markdown file: {target}")
        return [target]

    markdown_files: list[Path] = []
    ignore_patterns = _load_ignore_patterns(target, config)
    for candidate in target.rglob("*.md"):
        if _is_ignored(candidate, target, config, ignore_patterns):
            continue
        markdown_files.append(candidate)
    return sorted(path.resolve() for path in markdown_files)


def _is_ignored(path: Path, root: Path, config: AuditConfig, ignore_patterns: list[str]) -> bool:
    try:
        relative_parts = path.relative_to(root).parts
    except ValueError:
        relative_parts = path.parts
    parent_parts = relative_parts[:-1]
    for part in parent_parts:
        if part in IGNORED_DIRECTORIES:
            return True
        if not config.include_hidden and part.startswith("."):
            return True
    if _matches_project_ignore(relative_parts, ignore_patterns):
        return True
    return False


def _load_ignore_patterns(root: Path, config: AuditConfig) -> list[str]:
    ignore_file = root / config.ignore_file_name
    if not ignore_file.exists():
        return []
    try:
        lines = ignore_file.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise AuditInputError(f"Could not read {ignore_file}: {exc}") from exc
    patterns: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        patterns.append(stripped.lstrip("./"))
    return patterns


def _matches_project_ignore(relative_parts: tuple[str, ...], patterns: list[str]) -> bool:
    if not patterns:
        return False
    relative_path = "/".join(relative_parts)
    for pattern in patterns:
        normalized = pattern.replace("\\", "/")
        if normalized.endswith("/"):
            directory = normalized.rstrip("/")
            if relative_path == directory or relative_path.startswith(f"{directory}/"):
                return True
            continue
        if "/" in normalized:
            if (
                relative_path == normalized
                or relative_path.startswith(f"{normalized.rstrip('/')}/")
                or fnmatch(relative_path, normalized)
            ):
                return True
            continue
        if any(fnmatch(part, normalized) for part in relative_parts):
            return True
    return False


def _read_document(path: Path, config: AuditConfig, result: AuditResult) -> Document | None:
    max_bytes = config.max_file_size_kb * 1024
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise AuditInputError(f"Could not read file metadata for {path}: {exc}") from exc
    if size > max_bytes:
        result.issues.append(
            Issue(
                severity="warning",
                code="file-too-large",
                path=path,
                line=1,
                column=1,
                summary=f"Skipped Markdown file larger than {config.max_file_size_kb} KB.",
            )
        )
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AuditInputError(f"Could not read {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise AuditInputError(f"Could not decode {path} as UTF-8: {exc}") from exc
    return parse_document(path, text)


def _find_public_path_warnings(document: Document) -> list[Issue]:
    issues: list[Issue] = []
    in_fence = False
    fence_marker = ""
    for line_number, line in enumerate(document.text_lines, start=1):
        stripped = line.lstrip(" ")
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            continue
        if in_fence:
            continue
        issues.extend(
            _matches_to_issues(
                LOCAL_FILE_URL_RE.finditer(line),
                document.path,
                line_number,
                "local-file-url",
                "Document contains a file:// local path that is not suitable for public docs.",
            )
        )
        issues.extend(
            _matches_to_issues(
                POSIX_LOCAL_PATH_RE.finditer(line),
                document.path,
                line_number,
                "local-absolute-path",
                "Document contains an absolute local path that may not be suitable for public docs.",
            )
        )
        issues.extend(
            _matches_to_issues(
                WINDOWS_LOCAL_PATH_RE.finditer(line),
                document.path,
                line_number,
                "local-absolute-path",
                "Document contains an absolute local path that may not be suitable for public docs.",
            )
        )
    return issues


def _matches_to_issues(
    matches: object,
    path: Path,
    line_number: int,
    code: str,
    summary: str,
) -> list[Issue]:
    return [
        Issue(
            severity="warning",
            code=code,
            path=path,
            line=line_number,
            column=match.start() + 1,
            summary=summary,
            value=match.group(0),
            sensitive=True,
        )
        for match in matches
    ]


def _check_link(
    link: Link,
    document: Document,
    documents: dict[Path, Document],
    config: AuditConfig,
    result: AuditResult,
) -> list[Issue]:
    target = link.raw_target.strip()
    if not target:
        return [
            Issue(
                severity="error",
                code="empty-link",
                path=link.path,
                line=link.line,
                column=link.column,
                summary="Markdown link target is empty.",
            )
        ]

    if _looks_like_todo_target(target):
        return [
            Issue(
                severity="warning",
                code="todo-link",
                path=link.path,
                line=link.line,
                column=link.column,
                summary="Markdown link target looks like an unresolved placeholder.",
                value=target,
            )
        ]

    if _is_absolute_local_target(target):
        return [
            Issue(
                severity="warning",
                code="local-absolute-path",
                path=link.path,
                line=link.line,
                column=link.column,
                summary="Markdown link uses an absolute local path.",
                value=target,
                sensitive=True,
            )
        ]

    split = urlsplit(target)
    scheme = split.scheme.lower()
    if scheme in EXTERNAL_SCHEMES:
        return []
    if scheme == "file":
        return [
            Issue(
                severity="warning",
                code="local-file-url",
                path=link.path,
                line=link.line,
                column=link.column,
                summary="Markdown link uses a file:// local path.",
                value=target,
                sensitive=True,
            )
        ]
    if scheme:
        return [
            Issue(
                severity="warning",
                code="unsupported-scheme",
                path=link.path,
                line=link.line,
                column=link.column,
                summary="Markdown link uses a URL scheme this tool does not check.",
                value=target,
            )
        ]

    path_part = unquote(split.path)
    fragment = unquote(split.fragment)
    if not path_part and not fragment:
        return [
            Issue(
                severity="error",
                code="empty-link",
                path=link.path,
                line=link.line,
                column=link.column,
                summary="Markdown link target is empty.",
            )
        ]
    if not path_part and fragment == "":
        return []

    target_path = document.path if not path_part else (document.path.parent / path_part).resolve()
    if path_part and not target_path.exists():
        return [
            Issue(
                severity="error",
                code="missing-image" if link.kind == "image" else "missing-file",
                path=link.path,
                line=link.line,
                column=link.column,
                summary=(
                    "Image target does not exist."
                    if link.kind == "image"
                    else "Linked local file does not exist."
                ),
                value=target,
            )
        ]

    if fragment:
        return _check_anchor(link, target, target_path, fragment, documents, config, result)

    return []


def _check_anchor(
    link: Link,
    target: str,
    target_path: Path,
    fragment: str,
    documents: dict[Path, Document],
    config: AuditConfig,
    result: AuditResult,
) -> list[Issue]:
    if fragment.strip() == "":
        return [
            Issue(
                severity="error",
                code="empty-link",
                path=link.path,
                line=link.line,
                column=link.column,
                summary="Markdown link target has an empty anchor.",
                value=target,
            )
        ]

    if target_path.suffix.lower() != ".md":
        return [
            Issue(
                severity="warning",
                code="unchecked-anchor",
                path=link.path,
                line=link.line,
                column=link.column,
                summary="Anchor target is not a Markdown file, so it was not checked.",
                value=target,
            )
        ]

    target_document = documents.get(target_path)
    if target_document is None:
        target_document = _read_document(target_path, config, result)
        if target_document is None:
            return []
        documents[target_path] = target_document

    anchors = {heading.anchor for heading in target_document.headings}
    normalized_fragment = fragment.lstrip("#").strip()
    candidates = {normalized_fragment, normalized_fragment.lower(), slugify_heading(normalized_fragment)}
    if anchors.isdisjoint(candidates):
        return [
            Issue(
                severity="error",
                code="missing-anchor",
                path=link.path,
                line=link.line,
                column=link.column,
                summary="Markdown anchor does not match a heading in the target document.",
                value=target,
            )
        ]
    return []


def _looks_like_todo_target(target: str) -> bool:
    value = target.strip().strip("<>").strip().lower()
    value = value.strip("#")
    return value in TODO_TARGETS or value.startswith("todo:")


def _is_absolute_local_target(target: str) -> bool:
    if target.startswith("/"):
        return True
    return bool(re.match(r"^[A-Za-z]:\\", target))
