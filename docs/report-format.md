# Report Format

The CLI supports text, Markdown, and JSON reports.

## Text

Text output is intended for local terminals and simple CI logs.

## Markdown

Markdown output is intended for release notes, issue comments, or saved reports.

## JSON

JSON output contains a summary and an issue list. Each issue includes severity, rule, file, line, column, and summary. A `value` field is included only when values are enabled and the finding has a reportable value.

Use `--no-values` to remove raw target values from reports.

The JSON structure is stable enough for basic CI checks in the first version, but future versions may add fields.

## Output Files

When `--output` is used, existing files are not overwritten by default. Use `--force` when replacing a previous report is intentional.

Future CI-oriented formats may include SARIF, JUnit XML, or GitHub annotations, but those formats are not part of the first version.
