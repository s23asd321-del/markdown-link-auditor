"""Report renderers for CLI output."""

from __future__ import annotations

import json
from pathlib import Path

from .auditor import AuditResult
from .models import Issue


def render_report(result: AuditResult, report_format: str, *, no_values: bool = False) -> str:
    if report_format == "json":
        return render_json(result, no_values=no_values)
    if report_format == "markdown":
        return render_markdown(result, no_values=no_values)
    return render_text(result, no_values=no_values)


def render_text(result: AuditResult, *, no_values: bool = False) -> str:
    lines = [
        "markdown-link-auditor report",
        f"Scanned Markdown files: {len(result.scanned_files)}",
        f"Errors: {result.error_count}",
        f"Warnings: {result.warning_count}",
    ]
    if not result.issues:
        lines.append("No issues found.")
        return "\n".join(lines) + "\n"

    lines.append("")
    for issue in result.issues:
        location = _location(result.root, issue)
        detail = f"{location}: {issue.severity.upper()} {issue.code}: {issue.summary}"
        value = _public_value(issue, no_values=no_values)
        if value is not None:
            detail = f"{detail} [{value}]"
        lines.append(detail)
    return "\n".join(lines) + "\n"


def render_markdown(result: AuditResult, *, no_values: bool = False) -> str:
    lines = [
        "# markdown-link-auditor report",
        "",
        f"- Scanned Markdown files: {len(result.scanned_files)}",
        f"- Errors: {result.error_count}",
        f"- Warnings: {result.warning_count}",
        "",
    ]
    if not result.issues:
        lines.append("No issues found.")
        return "\n".join(lines) + "\n"

    lines.extend(["| File | Line | Severity | Rule | Summary | Value |", "| --- | ---: | --- | --- | --- | --- |"])
    for issue in result.issues:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_markdown(_relative_path(result.root, issue.path)),
                    str(issue.line),
                    issue.severity,
                    issue.code,
                    _escape_markdown(issue.summary),
                    _escape_markdown(_public_value(issue, no_values=no_values) or ""),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def render_json(result: AuditResult, *, no_values: bool = False) -> str:
    payload = {
        "summary": {
            "scanned_files": len(result.scanned_files),
            "errors": result.error_count,
            "warnings": result.warning_count,
        },
        "issues": [_issue_to_json(result.root, issue, no_values=no_values) for issue in result.issues],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _issue_to_json(root: Path, issue: Issue, *, no_values: bool) -> dict[str, object]:
    payload: dict[str, object] = {
        "severity": issue.severity,
        "rule": issue.code,
        "file": _relative_path(root, issue.path),
        "line": issue.line,
        "column": issue.column,
        "summary": issue.summary,
    }
    value = _public_value(issue, no_values=no_values)
    if value is not None:
        payload["value"] = value
    return payload


def _location(root: Path, issue: Issue) -> str:
    return f"{_relative_path(root, issue.path)}:{issue.line}:{issue.column}"


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _public_value(issue: Issue, *, no_values: bool) -> str | None:
    if no_values or issue.value is None:
        return None
    if issue.sensitive:
        return "redacted local path"
    return issue.value


def _escape_markdown(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
