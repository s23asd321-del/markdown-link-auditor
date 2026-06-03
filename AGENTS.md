# AGENTS

Guidance for automated coding agents working in this repository:

- Keep the project local-first and read-only.
- Do not add network checks, telemetry, auto-fix behavior, or web UI code.
- Do not introduce runtime third-party dependencies without a clear reason.
- Prefer Python standard library modules for the core package.
- Keep docs conservative: do not claim exact GitHub compatibility or complete issue detection.
- Keep examples fake and safe for public repositories.
- Run `python -m pytest` and `python -m markdown_link_auditor.cli check .` before proposing release changes.
