# Contributing

Thanks for helping improve `markdown-link-auditor`.

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
```

## Project Boundaries

- Keep runtime dependencies minimal.
- Do not add network access for link validation.
- Do not add auto-fix behavior without a separate design discussion.
- Do not add features that modify user Markdown files.
- Keep reports clear enough for CI logs and local terminal use.

## Pull Requests

Please include tests for behavior changes and update docs when rules or output formats change.
