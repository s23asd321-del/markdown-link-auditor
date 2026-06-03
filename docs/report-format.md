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
