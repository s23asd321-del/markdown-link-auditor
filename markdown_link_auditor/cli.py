"""Command-line interface for markdown-link-auditor."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .auditor import AuditConfig, AuditInputError, audit_path
from .reporters import render_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="markdown-link-audit",
        description="Audit local Markdown links, images, anchors, and public-readiness path issues.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="Check a Markdown file or directory.")
    check.add_argument("path", help="Markdown file or directory to scan.")
    check.add_argument(
        "--format",
        choices=("text", "markdown", "json"),
        default="text",
        help="Report format.",
    )
    check.add_argument("--output", help="Write the report to a file instead of stdout.")
    check.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings unless --fail-on is explicitly set.",
    )
    check.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden directories while scanning.",
    )
    check.add_argument(
        "--max-file-size-kb",
        type=int,
        default=512,
        help="Skip Markdown files larger than this size in KB.",
    )
    check.add_argument(
        "--no-values",
        action="store_true",
        help="Hide link values in reports.",
    )
    check.add_argument(
        "--fail-on",
        choices=("warning", "error"),
        default=None,
        help="Minimum severity that should produce exit code 1.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "check":
        fail_on = args.fail_on or ("warning" if args.strict else "error")
        try:
            result = audit_path(
                Path(args.path),
                AuditConfig(
                    include_hidden=args.include_hidden,
                    max_file_size_kb=args.max_file_size_kb,
                ),
            )
            report = render_report(result, args.format, no_values=args.no_values)
            if args.output:
                Path(args.output).write_text(report, encoding="utf-8")
            else:
                sys.stdout.write(report)
        except AuditInputError as exc:
            parser.exit(2, f"markdown-link-audit: {exc}\n")
        except OSError as exc:
            parser.exit(2, f"markdown-link-audit: could not write report: {exc}\n")

        if _should_fail(result.error_count, result.warning_count, fail_on):
            return 1
        return 0

    parser.exit(2, "markdown-link-audit: unknown command\n")
    return 2


def _should_fail(error_count: int, warning_count: int, fail_on: str) -> bool:
    if fail_on == "warning":
        return error_count > 0 or warning_count > 0
    return error_count > 0


if __name__ == "__main__":
    raise SystemExit(main())
