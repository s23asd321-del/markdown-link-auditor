# Design

The tool has three small layers:

- Markdown discovery and parsing.
- Local rule checks.
- Report rendering for text, Markdown, and JSON.

The parser is intentionally limited. It recognizes common inline links, images, reference-style link definitions, ATX headings, and fenced code blocks. It skips links inside fenced code blocks.

The auditor treats external schemes such as `http`, `https`, `mailto`, `tel`, and `data` as out of scope. Those targets are skipped without network access.

The CLI is read-only. It reports findings but does not edit, delete, move, or upload files.

## Project Ignore File

When a scanned directory contains `.markdown-link-auditor-ignore`, simple path patterns in that file are skipped. This is intentionally modest and should not be treated as a complete `.gitignore` implementation.
