# markdown-link-auditor

`markdown-link-auditor` is a local-first, read-only CLI for checking Markdown links, image paths, and heading anchors before publishing docs or running them in CI.

It is intentionally small: no network access, no external link probing, no crawler, no auto-fix mode, and no telemetry.

## Documentation

- [Overview](docs/overview.md)
- [Design](docs/design.md)
- [Rules](docs/rules.md)
- [Anchor slugs](docs/anchor-slugs.md)
- [Report format](docs/report-format.md)
- [Security and privacy](docs/security-and-privacy.md)
- [Release checklist](docs/release-checklist.md)

## What It Checks

- Relative Markdown links point to existing local files.
- Markdown image paths point to existing local files.
- Same-file anchors match real headings.
- Cross-file anchors match real headings in the target Markdown file.
- Empty link targets are reported.
- Duplicate headings that may produce anchor collisions are reported.
- Local absolute paths and local file URLs are reported without exposing their full values by default.
- Unresolved TODO-style link placeholders are reported.
- Unsupported URL schemes are reported as warnings.

## What It Does Not Do

- It does not check whether external links are online.
- It does not access the network.
- It does not crawl web pages.
- It does not call the GitHub API.
- It does not upload, delete, move, or modify user files.
- It is not a security scanner, secret scanner, or compliance tool.
- It does not guarantee that every link, anchor, or document is semantically correct.
- Its heading slug behavior is approximate GitHub-style behavior, not a promise of exact GitHub renderer compatibility.
- Redaction keeps reported local path values out of normal output, but it is not secret scanning.

## Install

For local development:

```bash
python -m pip install -e ".[dev]"
```

The runtime package has no third-party dependencies.

## Usage

Run directly from the source tree:

```bash
python -m markdown_link_auditor.cli check .
python -m markdown_link_auditor.cli check README.md
python -m markdown_link_auditor.cli check docs --format markdown
python -m markdown_link_auditor.cli check . --format json
python -m markdown_link_auditor.cli check . --output /tmp/markdown-link-report.md --format markdown
python -m markdown_link_auditor.cli check . --output /tmp/markdown-link-report.md --format markdown --force
```

After installation, the CLI entry point is also available:

```bash
markdown-link-audit check .
markdown-link-audit check docs --format json
markdown-link-audit check README.md --strict
```

## Report Examples

Text output:

```text
markdown-link-auditor report
Scanned Markdown files: 2
Errors: 0
Warnings: 0
No issues found.
```

Markdown output:

```markdown
# markdown-link-auditor report

- Scanned Markdown files: 2
- Errors: 0
- Warnings: 0
```

JSON output:

```json
{
  "issues": [],
  "summary": {
    "errors": 0,
    "scanned_files": 2,
    "warnings": 0
  }
}
```

Use `--no-values` when reports may be copied into public tickets or CI logs. It hides raw link targets from findings and only keeps file, line, rule, and summary fields.

## Options

| Option | Default | Description |
| --- | --- | --- |
| `--format text/markdown/json` | `text` | Selects report format. |
| `--output <file>` | stdout | Writes the report to a file. Existing files are not overwritten unless `--force` is used. |
| `--force` | off | Allows `--output` to overwrite an existing file. |
| `--strict` | off | Fails on warnings unless `--fail-on` is set. |
| `--include-hidden` | off | Includes hidden directories. |
| `--max-file-size-kb <number>` | `512` | Skips Markdown files above this size. |
| `--no-values` | off | Hides link values in reports. |
| `--fail-on warning/error` | `error` | Sets the minimum severity that returns exit code 1. |

## Exit Codes

| Code | Meaning |
| ---: | --- |
| 0 | No issue reached the configured fail threshold. |
| 1 | At least one issue reached the configured fail threshold. |
| 2 | CLI arguments, input path, read, or report write error. |

## Default Scan Behavior

Directories are scanned recursively for files ending in `.md`. A single Markdown file input scans only that file.

The scanner ignores common generated or dependency directories by default, including `.git`, `node_modules`, virtual environments, build outputs, cache directories, and hidden directories.

External URL schemes such as `http`, `https`, `mailto`, `tel`, and `data` are skipped. They are not fetched or validated.

If a `.markdown-link-auditor-ignore` file exists in the scanned directory, simple path patterns from that file are skipped. This repository uses it to keep intentionally broken examples out of the root self-check while still allowing direct checks of those examples.

## Rules

| Rule | Severity | Summary |
| --- | --- | --- |
| `missing-file` | error | A local link points to a missing file. |
| `missing-image` | error | A Markdown image points to a missing file. |
| `missing-anchor` | error | A Markdown anchor does not match a target heading. |
| `empty-link` | error | A link target is empty. |
| `undefined-reference` | error | A reference-style link has no matching definition. |
| `duplicate-heading` | warning | A heading may collide with an earlier generated anchor. |
| `local-absolute-path` | warning | A local absolute path appears in docs. |
| `local-file-url` | warning | A local file URL appears in docs. |
| `todo-link` | warning | A link target looks like an unresolved placeholder. |
| `unsupported-scheme` | warning | A link uses a URL scheme this tool does not check. |
| `file-too-large` | warning | A Markdown file was skipped because it exceeded the size limit. |
| `unchecked-anchor` | warning | A fragment target is not a Markdown file, so the anchor was not checked. |

## Markdown Support

Version 0.1 intentionally uses a small parser rather than a complete CommonMark implementation. It covers common inline links, images, same-file anchors, cross-file anchors, reference-style definitions, and fenced code blocks. Links inside fenced code blocks are skipped.

Future parser work should focus on accuracy for nested parentheses, escaped characters, complex reference links, and broader CommonMark fixtures while keeping the default behavior predictable.

## Examples

- [Good docs example](examples/good-docs/README.md) should pass with exit code 0.
- [Bad docs example](examples/bad-docs/README.md) intentionally demonstrates errors and warnings and should fail with exit code 1 under the default `--fail-on error` threshold.

## Development

```bash
python -m pytest
python -m markdown_link_auditor.cli check .
```

Continuous integration runs pytest, checks the good example, validates JSON output, and confirms the bad example fails as expected.

## Contributors

- s23asd321-del: project owner and maintainer
- OpenAI Codex: AI-assisted development support.

## Security, Privacy, Disclaimer, and License

See [SECURITY.md](SECURITY.md), [PRIVACY.md](PRIVACY.md), [DISCLAIMER.md](DISCLAIMER.md), and [LICENSE](LICENSE).
